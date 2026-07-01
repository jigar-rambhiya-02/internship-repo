"""
tests/test_evaluator.py

Integration-style tests for the evaluator module — uses mocking to avoid
real ChromaDB, PDF, and Groq calls in the CI test suite.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from production_rag.evaluator import save_results


def _make_flat_df():
    """Minimal flat eval dataframe matching the shape produced by run_eval_harness."""
    rows = []
    for config in ["naive", "reranked", "contextual", "both"]:
        for q_id in [1, 2]:
            rows.append({
                "question_id": q_id,
                "question": f"Sample question {q_id}",
                "config": config,
                "faithfulness": 0.75,
                "answer_relevancy": 0.80,
                "answer": "Sample answer.",
            })
    return pd.DataFrame(rows)


def test_save_results_creates_csv(tmp_path):
    df = _make_flat_df()
    csv_path = str(tmp_path / "results.csv")

    with patch("production_rag.evaluator.RESULTS_CSV", csv_path):
        save_results(df)

    import os
    assert os.path.exists(csv_path)


def test_save_results_correct_columns(tmp_path):
    df = _make_flat_df()
    csv_path = str(tmp_path / "results.csv")

    with patch("production_rag.evaluator.RESULTS_CSV", csv_path):
        save_results(df)

    result_df = pd.read_csv(csv_path)
    expected_cols = {
        "question_id", "question",
        "naive_faithfulness", "naive_relevance",
        "reranked_faithfulness", "reranked_relevance",
        "contextual_faithfulness", "contextual_relevance",
        "both_faithfulness", "both_relevance",
    }
    assert expected_cols.issubset(set(result_df.columns))


def test_save_results_row_count(tmp_path):
    df = _make_flat_df()
    csv_path = str(tmp_path / "results.csv")

    with patch("production_rag.evaluator.RESULTS_CSV", csv_path):
        save_results(df)

    result_df = pd.read_csv(csv_path)
    assert len(result_df) == 2  # One row per question_id
