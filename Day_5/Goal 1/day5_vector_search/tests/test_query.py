"""
Unit tests for vvs/query.py.

Covers the pure-logic pieces (manifest loading, chunk hydration, arg parsing)
without invoking live embedding, Vertex AI, or Groq calls.
"""

import csv
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vvs"))

from vvs.query import hydrate_chunk_metadata, load_manifest  # noqa: E402


def test_load_manifest_reads_csv_into_dict_keyed_by_doc_id():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["doc_id", "title", "year", "doc_type", "num_pages", "num_chunks"])
        writer.writeheader()
        writer.writerow({
            "doc_id": "abc123def456",
            "title": "Attention Is All You Need",
            "year": "2017",
            "doc_type": "arxiv_paper",
            "num_pages": "15",
            "num_chunks": "30",
        })
        temp_path = f.name

    try:
        manifest = load_manifest(temp_path)
        assert "abc123def456" in manifest
        assert manifest["abc123def456"]["title"] == "Attention Is All You Need"
    finally:
        os.remove(temp_path)


def test_load_manifest_missing_file_returns_empty_dict():
    manifest = load_manifest("/tmp/this_file_does_not_exist_12345.csv")
    assert manifest == {}


def test_hydrate_chunk_metadata_parses_doc_id_from_chunk_id():
    raw_results = [{"chunk_id": "abc123def456_chunk_0003", "distance": 0.87}]
    manifest = {
        "abc123def456": {
            "title": "Attention Is All You Need",
            "year": "2017",
            "doc_type": "arxiv_paper",
        }
    }

    enriched = hydrate_chunk_metadata(raw_results, manifest)

    assert len(enriched) == 1
    assert enriched[0]["doc_id"] == "abc123def456"
    assert enriched[0]["title"] == "Attention Is All You Need"
    assert enriched[0]["distance"] == 0.87


def test_hydrate_chunk_metadata_handles_missing_manifest_entry_gracefully():
    raw_results = [{"chunk_id": "unknown_doc_chunk_0000", "distance": 0.5}]
    manifest = {}

    enriched = hydrate_chunk_metadata(raw_results, manifest)

    assert enriched[0]["title"] == "unknown"
    assert enriched[0]["year"] == "unknown"
