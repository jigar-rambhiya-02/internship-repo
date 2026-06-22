import csv
import os
import sys

import arxiv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    EMBEDDING_MODEL,
    CHUNK_SIZE_TOKENS,
    CHUNK_OVERLAP_TOKENS,
    GCP_PROJECT_ID,
    GCP_REGION,
    MANIFEST_PATH,
    PDF_DATA_DIR,
    VERTEX_INDEX_ID,
    validate_settings,
)

from src.chunker import chunk_document
from src.embedder import embed_chunks
from src.pdf_parser import parse_pdf
from src.vector_store import upsert_chunks
from utils.logger import get_logger

logger = get_logger()

_SEARCH_QUERY = 'transformer architecture or large language models'
_TARGET_PAPER_COUNT = 10
_MANIFEST_COLUMNS = ['doc_id', 'title', 'year', 'doc_type', 'num_pages', 'num_chunks']


def download_corpus(target_count: int, output_dir: str) -> list:
    os.makedirs(output_dir, exist_ok = True)

    client = arxiv.Client()
    search = arxiv.Search(
        query = _SEARCH_QUERY,
        max_results = target_count,
        sorted_by = arxiv.SortCritersion.Relevance,
    )

    pdf_paths = []
    downloaded_count = 0
    skipped_count = 0

    for result in client.results(search):
        arxiv_id = result.get_short_id()
        safe_filename = f'{arxiv_id.replace('/', '-')}.pdf'
        destination_path = os.path.join(output_dir, safe_filename)

        if os.path.exists(destination_path):
            skipped_count += 1
            pdf_paths.append(destination_path)
            continue

        try:
            result.download_pdf(dirpath = output_dir, filename = safe_filename)
            downloaded_count += 1
            pdf_paths.append(destination_path)
            logger.info(f'Downloaded: "{result.title}" | arxiv_id = {arxiv_id}')
        except Exception as e:
            logger.error(f'Failed to download arxiv_id = {arxiv_id} | {e}')
            continue


    logger.info(
        f'Corpus Download Complete | Downloaded = {downloaded_count} | '
        f'already_present_skipped = {skipped_count} | total_available = {len(pdf_paths)}'
    )


def append_to_manifest(manifest_path: str, doc: dict, num_chunks: int) -> None:
    """
    Appends a single document's metadata row to the manifest CSV.
    Writes the header only if the file is currently empty.
    """
    file_is_empty = (not os.path.exists(manifest_path)) or os.path.getsize(manifest_path) == 0

    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)

    with open(manifest_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_MANIFEST_COLUMNS, extrasaction="ignore")
        if file_is_empty:
            writer.writeheader()
        writer.writerow({
            "doc_id": doc["doc_id"],
            "title": doc["title"],
            "year": doc["year"],
            "doc_type": doc["doc_type"],
            "num_pages": doc["num_pages"],
            "num_chunks": num_chunks,
        })


def run_ingestion() -> None:
    validate_settings()

    logger.info("=== Starting ingestion pipeline ===")

    pdf_paths = download_corpus(_TARGET_PAPER_COUNT, PDF_DATA_DIR)

    total_attempted = len(pdf_paths)
    successfully_ingested = 0
    failed_or_skipped = 0
    total_chunks_created = 0
    total_embeddings_pushed = 0

    for pdf_path in pdf_paths:
        doc = parse_pdf(pdf_path)
        if doc is None:
            failed_or_skipped += 1
            continue

        chunks = chunk_document(doc, chunk_size=CHUNK_SIZE_TOKENS, overlap=CHUNK_OVERLAP_TOKENS)
        if not chunks:
            logger.info(f"doc_id={doc['doc_id']} produced no chunks — skipping upsert and manifest entry.")
            failed_or_skipped += 1
            continue

        embedded_chunks = embed_chunks(chunks, model=EMBEDDING_MODEL)
        if not embedded_chunks:
            logger.error(f"doc_id={doc['doc_id']} produced zero successful embeddings — skipping.")
            failed_or_skipped += 1
            continue

        try:
            upserted_count = upsert_chunks(
                embedded_chunks,
                project=GCP_PROJECT_ID,
                region=GCP_REGION,
                index_id=VERTEX_INDEX_ID,
            )
        except Exception as e:
            logger.error(f"Upsert failed for doc_id={doc['doc_id']}: {e}. Skipping manifest entry.")
            failed_or_skipped += 1
            continue

        append_to_manifest(MANIFEST_PATH, doc, num_chunks=len(chunks))

        successfully_ingested += 1
        total_chunks_created += len(chunks)
        total_embeddings_pushed += upserted_count

    logger.info("=== Ingestion pipeline complete ===")
    logger.info(f"Total PDFs attempted:       {total_attempted}")
    logger.info(f"Successfully ingested:      {successfully_ingested}")
    logger.info(f"Failed/skipped:             {failed_or_skipped}")
    logger.info(f"Total chunks created:       {total_chunks_created}")
    logger.info(f"Total embeddings pushed:    {total_embeddings_pushed}")


if __name__ == "__main__":
    run_ingestion()