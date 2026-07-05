"""
Primary Phase 2 deliverable: the online query pipeline.

Orchestrates: embed question -> ANN lookup -> metadata hydration ->
optional Groq synthesis -> print results.

Run with:
    python vvs/query.py --question "What is self-attention?"
    python vvs/query.py --question "..." --year 2023 --top_k 10 --no-synthesis
"""

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (  # noqa: E402
    EMBEDDING_MODEL,
    GCP_PROJECT_ID,
    GCP_REGION,
    MANIFEST_PATH,
    TOP_K_RESULTS,
    VERTEX_DEPLOYED_INDEX_ID,
    VERTEX_INDEX_ENDPOINT_ID,
    validate_settings,
)
from src.embedder import embed_query  # noqa: E402
from src.groq_synthesizer import synthesize_answer  # noqa: E402
from src.vector_store import query_index  # noqa: E402
from utils.logger import get_logger  # noqa: E402

logger = get_logger()


def parse_args() -> argparse.Namespace:
    """Parses CLI arguments for query.py."""
    parser = argparse.ArgumentParser(description="Query the Day 5 vector search RAG pipeline.")
    parser.add_argument("--question", required=True, type=str, help="The search query string.")
    parser.add_argument("--year", required=False, type=str, default=None, help="Filter to a specific year, e.g. '2023'.")
    parser.add_argument("--doc_type", required=False, type=str, default=None, help="Filter to a specific doc_type.")
    parser.add_argument("--top_k", required=False, type=int, default=TOP_K_RESULTS, help="Number of chunks to retrieve.")
    parser.add_argument("--no-synthesis", dest="no_synthesis", action="store_true", help="Skip Groq synthesis; return raw chunks only.")
    return parser.parse_args()


def load_manifest(manifest_path: str) -> dict:
    """
    Loads the manifest CSV into a dict keyed by doc_id, once, at startup.

    Args:
        manifest_path: path to corpus_manifest.csv.

    Returns:
        dict: {doc_id: {"title": str, "year": str, "doc_type": str, ...}}
    """
    manifest = {}
    if not os.path.exists(manifest_path):
        logger.error(f"Manifest not found at {manifest_path}. Run ingest.py first.")
        return manifest

    with open(manifest_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            manifest[row["doc_id"]] = row

    return manifest


def hydrate_chunk_metadata(raw_results: list, manifest: dict) -> list:
    """
    Hydrates raw {chunk_id, distance} results with full document metadata
    looked up from the manifest, by parsing doc_id out of chunk_id.

    Args:
        raw_results: list of {"chunk_id": str, "distance": float}.
        manifest: dict keyed by doc_id, as returned by load_manifest().

    Returns:
        list[dict]: enriched chunk dicts with title, year, doc_type, page_number
            populated where available. page_number is not stored in the manifest
            (it is doc-level, not chunk-level), so it is reported as "unknown"
            here; the chunk_index suffix of chunk_id is included for reference.
    """
    enriched = []
    for result in raw_results:
        chunk_id = result["chunk_id"]
        doc_id = chunk_id.rsplit("_chunk_", 1)[0] if "_chunk_" in chunk_id else chunk_id
        doc_meta = manifest.get(doc_id, {})

        enriched.append({
            "chunk_id": chunk_id,
            "distance": result["distance"],
            "doc_id": doc_id,
            "title": doc_meta.get("title", "unknown"),
            "year": doc_meta.get("year", "unknown"),
            "doc_type": doc_meta.get("doc_type", "unknown"),
            "page_number": "see chunk_id index",
            "text": "(raw text not stored in manifest — re-fetch from index metadata or local chunk cache if needed)",
        })
    return enriched


def print_chunks(chunks: list) -> None:
    """Prints the top-K raw chunks with their metadata to stdout."""
    print("\n=== Top Retrieved Chunks ===")
    for i, chunk in enumerate(chunks, start=1):
        print(
            f"{i}. chunk_id={chunk['chunk_id']} | distance={chunk['distance']:.4f} | "
            f"title='{chunk['title']}' | year={chunk['year']} | doc_type={chunk['doc_type']}"
        )
    print()


def run_query() -> None:
    """Runs the full Phase 2 query pipeline end to end."""
    validate_settings()
    args = parse_args()

    manifest = load_manifest(MANIFEST_PATH)

    query_embedding = embed_query(args.question, model=EMBEDDING_MODEL)

    filter_namespaces = {}
    if args.year:
        filter_namespaces["year"] = args.year
    if args.doc_type:
        filter_namespaces["doc_type"] = args.doc_type

    raw_results = query_index(
        query_embedding=query_embedding,
        top_k=args.top_k,
        project=GCP_PROJECT_ID,
        region=GCP_REGION,
        index_endpoint_id=VERTEX_INDEX_ENDPOINT_ID,
        deployed_index_id=VERTEX_DEPLOYED_INDEX_ID,
        filter_namespaces=filter_namespaces or None,
    )

    enriched_chunks = hydrate_chunk_metadata(raw_results, manifest)

    print_chunks(enriched_chunks)

    synthesis_token_usage = "skipped (--no-synthesis)"
    if not args.no_synthesis:
        answer = synthesize_answer(args.question, enriched_chunks)
        print("=== Synthesized Answer ===")
        print(answer)
        print()
        synthesis_token_usage = "see output.log for token usage detail"

    logger.info(
        f"Query event complete | question='{args.question}' | filters={filter_namespaces} | "
        f"chunk_ids_returned={[c['chunk_id'] for c in enriched_chunks]} | "
        f"synthesis_token_usage={synthesis_token_usage}"
    )


if __name__ == "__main__":
    run_query()
