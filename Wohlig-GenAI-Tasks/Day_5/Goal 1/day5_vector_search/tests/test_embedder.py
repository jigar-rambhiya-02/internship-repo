"""
Unit tests for src/embedder.py.

All genai.embed_content() calls are mocked — no live API calls, no API key needed.
"""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.api_core.exceptions import ResourceExhausted  # noqa: E402

from src.embedder import embed_chunks, embed_query  # noqa: E402


def _fake_embedding_response(*args, **kwargs):
    return {"embedding": [0.1] * 768}


@patch("src.embedder.genai.embed_content", side_effect=_fake_embedding_response)
def test_embed_query_returns_768_dim_vector(mock_embed):
    result = embed_query("What is attention?", model="models/text-embedding-004")
    assert len(result) == 768
    mock_embed.assert_called_once()
    _, kwargs = mock_embed.call_args
    assert kwargs["task_type"] == "RETRIEVAL_QUERY"


@patch("src.embedder.genai.embed_content", side_effect=_fake_embedding_response)
def test_embed_chunks_adds_embedding_key_to_every_chunk(mock_embed):
    chunks = [
        {"chunk_id": "doc1_chunk_0000", "text": "chunk one text"},
        {"chunk_id": "doc1_chunk_0001", "text": "chunk two text"},
    ]
    result = embed_chunks(chunks, model="models/text-embedding-004", batch_size=20)

    assert len(result) == 2
    for chunk in result:
        assert "embedding" in chunk
        assert len(chunk["embedding"]) == 768


@patch("src.embedder.genai.embed_content", side_effect=_fake_embedding_response)
def test_embed_chunks_uses_retrieval_document_task_type(mock_embed):
    chunks = [{"chunk_id": "doc1_chunk_0000", "text": "some text"}]
    embed_chunks(chunks, model="models/text-embedding-004", batch_size=20)

    _, kwargs = mock_embed.call_args
    assert kwargs["task_type"] == "RETRIEVAL_DOCUMENT"


@patch("src.embedder.time.sleep", return_value=None)
@patch(
    "src.embedder.genai.embed_content",
    side_effect=[ResourceExhausted("quota exceeded")] * 6 + [{"embedding": [0.1] * 768}],
)
def test_embed_query_retries_on_resource_exhausted_then_raises_if_never_succeeds(mock_embed, mock_sleep):
    try:
        embed_query("test question", model="models/text-embedding-004")
        assert False, "Expected ResourceExhausted to be raised after exhausting retries"
    except ResourceExhausted:
        pass
    # 1 initial attempt + 5 retries = 6 calls before giving up
    assert mock_embed.call_count == 6
