# tests/test_judges.py
from unittest.mock import MagicMock

from eval.judges import judge_faithfulness


def test_judge_faithfulness_perfect_score():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"score": 1.0, "reasoning": "All claims supported."}'
    mock_client.chat.completions.create.return_value = mock_response

    result = judge_faithfulness(
        question="What is the policy?",
        answer="The policy is X.",
        retrieved_chunks=["The policy is X."],
        ground_truth_answer="The policy is X.",
        ground_truth_chunk_ids=["chunk_1"],
        retrieved_chunk_ids=["chunk_1"],
        client=mock_client,
    )
    assert result["score"] == 1.0
    assert result["reasoning"] == "All claims supported."


def test_judge_faithfulness_api_failure():
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    result = judge_faithfulness(
        question="What is the policy?",
        answer="The policy is X.",
        retrieved_chunks=["The policy is X."],
        ground_truth_answer="The policy is X.",
        ground_truth_chunk_ids=["chunk_1"],
        retrieved_chunk_ids=["chunk_1"],
        client=mock_client,
    )
    assert result["score"] is None
    assert result["reasoning"] == "JUDGE_ERROR"


def test_score_clamping():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"score": 1.5, "reasoning": "Too high"}'
    mock_client.chat.completions.create.return_value = mock_response

    result = judge_faithfulness(
        question="What is the policy?",
        answer="The policy is X.",
        retrieved_chunks=["The policy is X."],
        ground_truth_answer="The policy is X.",
        ground_truth_chunk_ids=["chunk_1"],
        retrieved_chunk_ids=["chunk_1"],
        client=mock_client,
    )
    assert result["score"] == 1.0
