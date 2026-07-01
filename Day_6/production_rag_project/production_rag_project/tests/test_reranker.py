"""
tests/test_reranker.py

Unit tests for the ReRanker class — focuses on the local BM25 + cosine fallback,
which runs without any GCP credentials.
"""

import pytest
from production_rag.reranker import ReRanker


@pytest.fixture
def sample_chunks():
    return [
        {"chunk_id": "a1", "text": "Annual revenue grew by twelve percent in fiscal year.", "score": 0.85},
        {"chunk_id": "a2", "text": "The board approved a share repurchase program worth five hundred million.", "score": 0.80},
        {"chunk_id": "a3", "text": "Operating expenses increased due to higher headcount in engineering.", "score": 0.75},
        {"chunk_id": "a4", "text": "Customer satisfaction scores reached an all-time high this quarter.", "score": 0.70},
        {"chunk_id": "a5", "text": "Capital expenditures were focused on data centre infrastructure.", "score": 0.65},
        {"chunk_id": "a6", "text": "Revenue from international markets outpaced domestic growth rates.", "score": 0.60},
    ]


def test_local_reranker_returns_top_k(sample_chunks):
    reranker = ReRanker()
    result = reranker._rerank_local("revenue growth", sample_chunks, top_k=3)
    assert len(result) == 3


def test_local_reranker_adds_rerank_score(sample_chunks):
    reranker = ReRanker()
    result = reranker._rerank_local("revenue growth", sample_chunks, top_k=3)
    for chunk in result:
        assert "rerank_score" in chunk
        assert 0.0 <= chunk["rerank_score"] <= 1.0


def test_local_reranker_sorted_descending(sample_chunks):
    reranker = ReRanker()
    result = reranker._rerank_local("revenue growth", sample_chunks, top_k=4)
    scores = [c["rerank_score"] for c in result]
    assert scores == sorted(scores, reverse=True)


def test_rerank_empty_input():
    reranker = ReRanker()
    result = reranker.rerank("some query", [], top_k=5)
    assert result == []


def test_rerank_fewer_chunks_than_top_k(sample_chunks):
    reranker = ReRanker()
    result = reranker.rerank("revenue", sample_chunks[:2], top_k=5)
    assert len(result) == 2
