import hashlib
import os
import re
import unicodedata

import pypdf
from pypdf.errors import PdfReadError

from utils.logger import get_logger

logger = get_logger()

_MIN_WORDS_PER_LINE = 3

def clean_text(text : str) -> str:

    if not text:
        return ''

    text = text.replace('\x00','')
    text = unicodedata.normalize('NFKC', text)

    cleaned_lines = []
    for line in text.split('\n'):
        collapsed = re.sub(r'\s+', ' ', line).strip()
        if not collapsed:
            continue
        cleaned_lines.append(collapsed)
    
    return '\n'.join(cleaned_lines)

def _compute_doc_id(pdf_path: str) -> str:
    sha256 = hashlib.sha256()

    with open(pdf_path, 'rb') as f:
        for block in iter(lambda: f.read(65536), b''):
            sha256.update(block)

    return sha256.hexdigest()[:12]

def _extract_title(reader: 'pypdf.PdfReader', pdf_path: str) -> str:
    try:
        metadata = reader.metadata
        if metadata is not None and metadata.title:
            title = str(metadata.title).strip()

            if title:
                return title
    
    except Exception:
        pass
    return os.path.splittext(os.path.basename(pdf_path))[0]

def _extract_year(reader: 'pypdf.PdfReader') -> int:
    try:
        metadata = reader.metadata
        if metadata is None:
            return 0
        
        raw_date = metadata.get('/CreationDate') or metadata.get('/ModDate')
        if not raw_date:
            return 0
        
        match = re.search(fr'D:(\d{4})', str(raw_date))
        if match:
            return int(match.group(1))

        return 0
    except Exception:
        return 0

def parse_pdf(pdf_path: str) -> dict:
    logger.info(f'Parsing PDF: {pdf_path}')

    try:
        doc_id = _compute_doc_id(pdf_path)
    
    except (OSError, IOError) as e:
        logger.error(f'Failed to read file for hashing: {pdf_path} | {e}')
        return None

    try:
        reader = pypdf.PdfReader(pdf_path)
    except PdfReadError as e:
        logger.error(f'pypdf failed to read PDF (corrupt or encrypted): {pdf_path} | {e}')
        return None
    except (OSError, IOError) as e:
        logger.error(f'File I/O error opening PDF: {pdf_path} | {e}')
        return None

    num_pages = len(reader.pages)
    logger.info(f'Found {num_pages} pages in {pdf_path} | doc_id = {doc_id}')

    pages = []
    for page_number, page in enumerate(reader.pages, start = 1):
        try:
            raw_text = page.extract_text() or ''
        except Exception as e:
            logger.error(f'Failed to extract text from page {page_number} of {pdf_path} | {e}')
            raw_text = ''
        
        pages.append({
            'page_number':page_number,
            'text': clean_text(raw_text),
        })
    
    title = _extract_title(reader, pdf_path)
    year = _extract_year(reader)

    return {
        'doc_id': doc_id,
        'title': title,
        'year': year,
        'doc_type': 'arxiv_paper',
        'num_pages': num_pages,
        'pages':pages,
    }
    