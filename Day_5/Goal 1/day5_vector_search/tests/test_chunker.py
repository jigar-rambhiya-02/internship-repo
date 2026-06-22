"""
Unit tests for src/chunker.py.

No network calls — chunk_document() is pure computation over tiktoken
encodings, so these tests run fully offline.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chunker import chunk_document  # noqa: E402


def _make_doc(text: str, num_pages: int = 1) -> dict:
    """Builds a minimal doc dict for testing, all text on page 1."""
    return {
        "doc_id": "abc123def456",
        "title": "Test Document",
        "year": 2023,
        "doc_type": "arxiv_paper",
        "num_pages": num_pages,
        "pages": [{"page_number": 1, "text": text}],
    }


def test_chunk_document_produces_expected_chunk_count():
    # ~1500 tokens of repeated text, chunk_size=512, overlap=64 -> stride=448
    long_text = " ".join(["word"] * 1500)
    doc = _make_doc(long_text)

    chunks = chunk_document(doc, chunk_size=512, overlap=64)

    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk["token_count"] <= 512
        assert chunk["doc_id"] == "abc123def456"


def test_chunk_document_chunk_ids_are_sequential_and_zero_padded():
    long_text = " ".join(["word"] * 1500)
    doc = _make_doc(long_text)

    chunks = chunk_document(doc, chunk_size=512, overlap=64)

    for i, chunk in enumerate(chunks):
        assert chunk["chunk_id"] == f"abc123def456_chunk_{i:04d}"


def test_chunk_document_skips_degenerate_short_documents():
    short_text = "Too short."
    doc = _make_doc(short_text)

    chunks = chunk_document(doc, chunk_size=512, overlap=64)

    # Fewer than 20 tokens total -> should produce zero chunks.
    assert chunks == []


def test_chunk_document_raises_on_invalid_overlap():
    doc = _make_doc("some text here for testing purposes only")
    try:
        chunk_document(doc, chunk_size=100, overlap=100)
        assert False, "Expected ValueError for overlap >= chunk_size"
    except ValueError:
        pass


def test_chunk_document_empty_pages_returns_empty_list():
    doc = _make_doc("")
    doc["pages"] = []
    chunks = chunk_document(doc, chunk_size=512, overlap=64)
    assert chunks == []
