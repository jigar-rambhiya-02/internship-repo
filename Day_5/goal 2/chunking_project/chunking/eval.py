"""
chunking/eval.py

Full evaluation pipeline for chunking strategy comparison.
Run: python -m chunking.eval
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config.settings import (
    CORPUS_DIR,
    TEST_SET_PATH,
    RESULTS_PATH,
    WINNER_PATH,
    CHUNK_SIZE_TOKENS,
    OVERLAP_TOKENS,
    MAX_SEMANTIC_TOKENS,
    OVERLAP_SENTENCES,
    TOP_K_SMALL,
    TOP_K_LARGE,
)
from chunking.strategies import fixed_size, sentence_aware, semantic
from utils.io_utils import load_corpus, iter_jsonl, write_results_csv
from utils.logging_utils import setup_logging
from utils.groq_client import chat_complete

setup_logging()
logger = logging.getLogger(__name__)

STRATEGIES = {
    "fixed": lambda text, doc_id: fixed_size(
        text, doc_id, chunk_size=CHUNK_SIZE_TOKENS, overlap=OVERLAP_TOKENS
    ),
    "sentence": lambda text, doc_id: sentence_aware(
        text, doc_id, target_tokens=CHUNK_SIZE_TOKENS, overlap_sentences=OVERLAP_SENTENCES
    ),
    "semantic": lambda text, doc_id: semantic(
        text, doc_id, max_tokens=MAX_SEMANTIC_TOKENS
    ),
}


# ── Indexing ───────────────────────────────────────────────────────────────────

def build_index(chunks: list[dict[str, Any]]) -> tuple[TfidfVectorizer, np.ndarray, list[str]]:
    """
    Build a TF-IDF index from a list of chunks.

    Returns:
        (fitted_vectorizer, tfidf_matrix, chunk_id_list)

    Raises:
        ValueError: If chunks list is empty.
    """
    if not chunks:
        raise ValueError("Cannot build index from empty chunk list.")

    texts = [c["text"] for c in chunks]
    chunk_ids = [c["chunk_id"] for c in chunks]

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_features=50_000,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(texts)
    logger.info("Built TF-IDF index: %d chunks, %d features", matrix.shape[0], matrix.shape[1])
    return vectorizer, matrix, chunk_ids


# ── Retrieval ──────────────────────────────────────────────────────────────────

def retrieve(
    query: str,
    vectorizer: TfidfVectorizer,
    matrix: np.ndarray,
    chunk_ids: list[str],
    top_k: int,
) -> list[str]:
    """
    Retrieve top_k chunk IDs for a query using TF-IDF cosine similarity.

    Raises:
        ValueError: If top_k > number of indexed chunks.
    """
    if top_k > len(chunk_ids):
        raise ValueError(
            f"top_k={top_k} exceeds total indexed chunks ({len(chunk_ids)}). "
            "Reduce top_k or index more documents."
        )
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, matrix).flatten()
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [chunk_ids[i] for i in top_indices]


# ── Recall Scoring ─────────────────────────────────────────────────────────────

def recall_at_k(retrieved: list[str], ground_truth: list[str]) -> float:
    """
    Compute recall@k.

    recall@k = |retrieved ∩ ground_truth| / |ground_truth|

    Raises:
        ValueError: If ground_truth is empty.
    """
    if not ground_truth:
        raise ValueError(
            "Ground truth chunk list is empty. "
            "Check test_set.jsonl for rows with empty 'ground_truth_chunk_ids'."
        )
    hits = len(set(retrieved) & set(ground_truth))
    return hits / len(ground_truth)


# ── Winner Analysis ────────────────────────────────────────────────────────────

def _strategy_key(strategy: str, k: int) -> str:
    return f"{strategy}_recall_{k}"


def compute_aggregate_scores(rows: list[dict]) -> dict[str, dict[str, float]]:
    """Compute mean recall@5 and recall@10 per strategy."""
    strategies = ["fixed", "sentence", "semantic"]
    ks = [TOP_K_SMALL, TOP_K_LARGE]
    scores: dict[str, dict[str, float]] = {}

    for strategy in strategies:
        scores[strategy] = {}
        for k in ks:
            key = _strategy_key(strategy, k)
            values = [row[key] for row in rows]
            scores[strategy][f"mean_recall@{k}"] = round(sum(values) / len(values), 4)

    return scores


def write_winner_md(
    path: Path,
    aggregate: dict[str, dict[str, float]],
    rows: list[dict],
) -> None:
    """Write winner.md with aggregate scores and recommendation."""

    # Determine winner by mean recall@5 (primary) and recall@10 (tiebreaker)
    def sort_key(item: tuple[str, dict]) -> tuple[float, float]:
        strategy, scores = item
        return (scores[f"mean_recall@{TOP_K_SMALL}"], scores[f"mean_recall@{TOP_K_LARGE}"])

    ranked = sorted(aggregate.items(), key=sort_key, reverse=True)
    winner = ranked[0][0]
    runner_up = ranked[1][0]
    last = ranked[2][0]

    # Use Groq to generate a human-readable explanation
    explanation_prompt = f"""
You are a RAG systems expert. Given these chunking evaluation results, write a concise
2-paragraph explanation of why '{winner}' won and what this means for production use.
Be specific. Mention corpus structure as a factor.

Results:
{json.dumps(aggregate, indent=2)}

Return only the 2-paragraph explanation. No headers, no bullet points.
"""
    try:
        explanation = chat_complete(
            system_prompt="You are a precise technical writer specializing in RAG systems.",
            user_message=explanation_prompt,
        )
    except Exception as exc:
        logger.warning("Groq explanation generation failed: %s. Using fallback.", exc)
        explanation = (
            f"The '{winner}' strategy achieved the highest mean recall, "
            "suggesting it produces chunks best aligned with the query vocabulary in this corpus. "
            "Manual review of low-scoring questions is recommended to identify systematic failure patterns."
        )

    content = f"""# Chunking Strategy Evaluation: Winner Analysis

## Aggregate Scores

| Strategy | mean_recall@{TOP_K_SMALL} | mean_recall@{TOP_K_LARGE} |
|---|---|---|
"""
    for strategy, scores in ranked:
        marker = " ✅ WINNER" if strategy == winner else ""
        content += (
            f"| `{strategy}`{marker} "
            f"| {scores[f'mean_recall@{TOP_K_SMALL}']:.4f} "
            f"| {scores[f'mean_recall@{TOP_K_LARGE}']:.4f} |\n"
        )

    content += f"""
## Recommended Chunker: `{winner}`

{explanation}

## Rule of Thumb

| Corpus Type | Recommended Strategy | Reasoning |
|---|---|---|
| Markdown / structured docs with headings | `semantic` | Headings define natural topic boundaries; chunks map to coherent sections |
| Plain prose, articles, transcripts | `sentence` | Sentence boundaries preserve grammatical coherence without relying on formatting |
| Unstructured text, logs, code, tables | `fixed` | No reliable boundaries exist; consistent size reduces retrieval variance |
| Mixed corpora | `sentence` | Safest general fallback; degrades gracefully on both structured and unstructured text |

## Per-Question Breakdown

Questions where the winner failed (recall@{TOP_K_SMALL} = 0.0):

"""
    winner_key = _strategy_key(winner, TOP_K_SMALL)
    failed = [r for r in rows if r[winner_key] == 0.0]
    if failed:
        for row in failed:
            content += f"- `{row['question_id']}`: {row.get('question', 'N/A')}\n"
    else:
        content += f"_None — {winner} achieved non-zero recall@{TOP_K_SMALL} on all questions._\n"

    content += f"""
## Methodology Notes

- **Vector search:** TF-IDF with cosine similarity (scikit-learn). Lexical matching only.
- **Recall formula:** `|retrieved_k ∩ ground_truth| / |ground_truth|`
- **Corpus subset:** 50 documents from `data/corpus/`
- **Test set:** 25 questions with manually verified ground-truth chunk IDs
- **Chunk size target:** {CHUNK_SIZE_TOKENS} tokens (fixed/sentence), {MAX_SEMANTIC_TOKENS} tokens max (semantic)

> **Production note:** TF-IDF retrieval underestimates semantic chunking's advantage in production,
> because dense embeddings better capture meaning across paraphrase boundaries where semantic chunks excel.
> If this experiment is reproduced with dense embeddings (e.g., `all-MiniLM-L6-v2`), expect
> the gap between semantic and fixed-size to widen.
"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    logger.info("Winner analysis written to %s", path)


# ── Main Runner ────────────────────────────────────────────────────────────────

def main() -> None:
    logger.info("=== Chunking Strategy Evaluation Pipeline START ===")

    # 1. Load corpus
    corpus = load_corpus(CORPUS_DIR)
    doc_ids = list(corpus.keys())[:50]  # Limit to 50 for cost control
    logger.info("Using %d documents for evaluation", len(doc_ids))

    # 2. Chunk all documents with all strategies
    all_chunks: dict[str, list[dict[str, Any]]] = {name: [] for name in STRATEGIES}

    for doc_id in doc_ids:
        text = corpus[doc_id]
        for strategy_name, chunker in STRATEGIES.items():
            chunks = chunker(text, doc_id)
            all_chunks[strategy_name].extend(chunks)

    for name, chunks in all_chunks.items():
        logger.info("Strategy '%s': %d total chunks across %d docs", name, len(chunks), len(doc_ids))

    # 3. Build TF-IDF index per strategy
    indexes: dict[str, tuple[TfidfVectorizer, np.ndarray, list[str]]] = {}
    for name, chunks in all_chunks.items():
        logger.info("Building index for strategy '%s'...", name)
        indexes[name] = build_index(chunks)

    # 4. Load test set
    test_questions = list(iter_jsonl(TEST_SET_PATH))
    if len(test_questions) != 25:
        raise ValueError(
            f"Expected exactly 25 test questions, found {len(test_questions)}. "
            f"Check {TEST_SET_PATH}."
        )
    logger.info("Loaded %d test questions", len(test_questions))

    # 5. Evaluate
    result_rows: list[dict] = []

    for question_obj in test_questions:
        qid = question_obj.get("question_id")
        question = question_obj.get("question")
        gt_chunk_ids: dict[str, list[str]] = question_obj.get("ground_truth_chunk_ids", {})

        if not qid or not question:
            raise ValueError(
                f"Malformed test question — missing 'question_id' or 'question': {question_obj}"
            )
        if not isinstance(gt_chunk_ids, dict):
            raise ValueError(
                f"Question '{qid}': 'ground_truth_chunk_ids' must be a dict mapping "
                f"strategy name to list of chunk IDs. Got: {type(gt_chunk_ids)}"
            )

        row: dict[str, Any] = {"question_id": qid, "question": question}

        for strategy_name, (vectorizer, matrix, chunk_ids) in indexes.items():
            gt = gt_chunk_ids.get(strategy_name, [])
            if not gt:
                logger.warning(
                    "No ground truth for strategy '%s', question '%s'. "
                    "Recall will be 0.0.", strategy_name, qid
                )

            retrieved_5 = retrieve(question, vectorizer, matrix, chunk_ids, TOP_K_SMALL)
            retrieved_10 = retrieve(question, vectorizer, matrix, chunk_ids, TOP_K_LARGE)

            row[_strategy_key(strategy_name, TOP_K_SMALL)] = (
                recall_at_k(retrieved_5, gt) if gt else 0.0
            )
            row[_strategy_key(strategy_name, TOP_K_LARGE)] = (
                recall_at_k(retrieved_10, gt) if gt else 0.0
            )

        result_rows.append(row)
        logger.info(
            "Scored question '%s': fixed@5=%.2f sentence@5=%.2f semantic@5=%.2f",
            qid,
            row[_strategy_key("fixed", TOP_K_SMALL)],
            row[_strategy_key("sentence", TOP_K_SMALL)],
            row[_strategy_key("semantic", TOP_K_SMALL)],
        )

    # 6. Write results CSV
    # Drop 'question' column from CSV output; keep only IDs and scores
    csv_rows = [
        {k: v for k, v in r.items() if k != "question"} for r in result_rows
    ]
    write_results_csv(RESULTS_PATH, csv_rows)

    # 7. Compute aggregate and write winner.md
    aggregate = compute_aggregate_scores(result_rows)
    write_winner_md(WINNER_PATH, aggregate, result_rows)

    logger.info("=== Chunking Strategy Evaluation Pipeline COMPLETE ===")
    logger.info("Results: %s", RESULTS_PATH)
    logger.info("Winner analysis: %s", WINNER_PATH)


if __name__ == "__main__":
    main()
