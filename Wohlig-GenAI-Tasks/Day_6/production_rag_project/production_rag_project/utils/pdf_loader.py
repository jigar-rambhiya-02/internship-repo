import hashlib
import pdfplumber
from utils.logger import setup_logger

logger = setup_logger(__name__)


def load_and_chunk_pdf(
    pdf_path: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """
    Load a PDF and split its text content into overlapping word-based chunks.

    Args:
        pdf_path:   Path to the PDF file.
        chunk_size: Target number of words per chunk.
        overlap:    Number of words to repeat at the start of each successive chunk.

    Returns:
        List of dicts, each containing:
            chunk_id (str):  Deterministic hash-based unique ID.
            text     (str):  Chunk text content.
            page     (int):  Source page number (1-indexed).
            source   (str):  pdf_path value for traceability.
    """
    chunks: list[dict] = []
    page_count = 0

    logger.info(f"Loading PDF: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        logger.info(f"PDF has {page_count} pages.")

        for page_num, page in enumerate(pdf.pages, start=1):
            raw_text = page.extract_text()
            if not raw_text:
                logger.debug(f"Page {page_num}: no extractable text, skipping.")
                continue

            words = raw_text.split()
            start = 0

            while start < len(words):
                end = start + chunk_size
                chunk_words = words[start:end]
                chunk_text = " ".join(chunk_words)

                # Deterministic ID: hash of (source path + page + start word index)
                id_source = f"{pdf_path}::page{page_num}::start{start}"
                chunk_id = hashlib.md5(id_source.encode()).hexdigest()[:16]

                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "text": chunk_text,
                        "page": page_num,
                        "source": pdf_path,
                    }
                )

                if end >= len(words):
                    break
                start = end - overlap  # slide window with overlap

    logger.info(
        f"Chunking complete: {len(chunks)} chunks from {page_count} pages "
        f"(chunk_size={chunk_size}, overlap={overlap})."
    )
    return chunks
