# tests/test_rag_bot.py
from unittest.mock import MagicMock, patch

from src.rag_bot import generate_answer, retrieve


def test_generate_answer_uses_context_only():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test answer"
    mock_client.chat.completions.create.return_value = mock_response

    question = "What is the policy?"
    context_chunks = ["The remote work policy allows 2 days per week."]

    result = generate_answer(question, context_chunks, mock_client)

    call_args = mock_client.chat.completions.create.call_args
    messages = call_args[1]["messages"]
    prompt_content = messages[1]["content"]
    assert "The remote work policy allows 2 days per week." in prompt_content
    assert "You are a grounded assistant" in messages[0]["content"]
    assert result == "Test answer"


def test_retrieve_returns_correct_structure():
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [["chunk1", "chunk2"]],
        "ids": [["id1", "id2"]],
    }

    with patch("src.rag_bot._get_embedder") as mock_get_embedder:
        mock_embedder = MagicMock()
        mock_array = MagicMock()
        mock_array.tolist.return_value = [[0.1, 0.2, 0.3]]
        mock_embedder.encode.return_value = mock_array
        mock_get_embedder.return_value = mock_embedder

        result = retrieve("test query", mock_collection, 2)

    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], list)
    assert isinstance(result[1], list)
    assert result[0] == ["chunk1", "chunk2"]
    assert result[1] == ["id1", "id2"]
