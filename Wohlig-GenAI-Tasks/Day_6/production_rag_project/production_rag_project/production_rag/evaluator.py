"""
production_rag/evaluator.py

RAGAS-based evaluation harness for all four RAG pipeline configurations.
Runs faithfulness and answer_relevancy metrics across all eval questions and saves
a comparison CSV to production_rag/results.csv.

Run as:
    python -m production_rag.evaluator
"""

import os
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from sentence_transformers import SentenceTransformer

from config.settings import (
    EVAL_QUESTIONS,
    EVAL_GROUND_TRUTHS,
    CORPUS_PDF_PATH,
    CHROMA_PERSIST_DIR,
    EMBED_MODEL,
    RESULTS_CSV,
)
from utils.logger import setup_logger
from utils.pdf_loader import load_and_chunk_pdf
from utils.chroma_store import get_or_create_collection, upsert_chunks
from production_rag.pipeline import RAGPipeline

logger = setup_logger(__name__)

CONFIGS = ["naive", "reranked", "contextual", "both"]


# ── Indexing helpers ──────────────────────────────────────────────────────────

def index_naive_corpus() -> None:
    """
    Load the PDF, embed all chunks, and upsert them into the 'naive_corpus'
    ChromaDB collection. Safe to call multiple times (upsert is idempotent).
    """
    logger.info("Indexing naive corpus...")
    chunks = load_and_chunk_pdf(CORPUS_PDF_PATH)
    collection = get_or_create_collection(
        collection_name="naive_corpus",
        persist_dir=CHROMA_PERSIST_DIR,
    )
    embed_model = SentenceTransformer(EMBED_MODEL)
    embeddings = [
        embed_model.encode(c["text"], convert_to_numpy=True).tolist()
        for c in chunks
    ]
    upsert_chunks(collection, chunks, embeddings)
    logger.info(f"Naive corpus indexed: {len(chunks)} chunks in 'naive_corpus'.")


# ── Eval harness ──────────────────────────────────────────────────────────────

def run_eval_harness() -> pd.DataFrame:
    """
    Run RAGAS evaluation across all 4 configurations and all eval questions.

    For each (config, question) pair:
      - Runs RAGPipeline(config).run(question)
      - Builds a RAGAS Dataset from the result
      - Evaluates faithfulness and answer_relevancy
      - Appends a result row

    Returns:
        pd.DataFrame with columns:
            question_id, question, config, faithfulness, answer_relevancy, answer
    """
    rows = []
    total = len(CONFIGS) * len(EVAL_QUESTIONS)
    completed = 0

    for config in CONFIGS:
        logger.info(f"=== Evaluating config: {config.upper()} ===")
        pipeline = RAGPipeline(config=config)

        for q_idx, (question, ground_truth) in enumerate(
            zip(EVAL_QUESTIONS, EVAL_GROUND_TRUTHS), start=1
        ):
            logger.info(
                f"[{config}] Q{q_idx}/{len(EVAL_QUESTIONS)}: '{question[:60]}'"
            )

            try:
                result = pipeline.run(question)
                answer = result["answer"]
                context_texts = [c["text"] for c in result["retrieved_chunks"]]

                # Build RAGAS dataset for this single example
                ragas_data = {
                    "question": [question],
                    "answer": [answer],
                    "contexts": [context_texts],
                    "ground_truth": [ground_truth],
                }
                dataset = Dataset.from_dict(ragas_data)

                scores = evaluate(
                    dataset,
                    metrics=[faithfulness, answer_relevancy],
                )

                faith_score = float(scores["faithfulness"])
                rel_score = float(scores["answer_relevancy"])

            except Exception as exc:
                logger.error(
                    f"Eval failed for config='{config}', Q{q_idx}: "
                    f"{type(exc).__name__}: {exc}. Recording NaN scores."
                )
                faith_score = float("nan")
                rel_score = float("nan")
                answer = "EVAL_ERROR"

            rows.append(
                {
                    "question_id": q_idx,
                    "question": question,
                    "config": config,
                    "faithfulness": faith_score,
                    "answer_relevancy": rel_score,
                    "answer": answer,
                }
            )
            completed += 1
            logger.info(
                f"Progress: {completed}/{total} | "
                f"faithfulness={faith_score:.3f}, answer_relevancy={rel_score:.3f}"
            )

    df = pd.DataFrame(rows)
    logger.info("Eval harness complete.")
    return df


# ── Results output ─────────────────────────────────────────────────────────────

def save_results(df: pd.DataFrame) -> None:
    """
    Pivot the flat eval dataframe so each row is a question and each column
    is a (config, metric) combination. Saves to RESULTS_CSV.

    Output columns:
        question_id, question,
        naive_faithfulness, naive_relevance,
        reranked_faithfulness, reranked_relevance,
        contextual_faithfulness, contextual_relevance,
        both_faithfulness, both_relevance
    """
    pivot_rows = []

    for q_id in df["question_id"].unique():
        q_df = df[df["question_id"] == q_id]
        question = q_df["question"].iloc[0]
        row: dict = {"question_id": int(q_id), "question": question}

        for config in CONFIGS:
            config_row = q_df[q_df["config"] == config]
            if not config_row.empty:
                row[f"{config}_faithfulness"] = round(
                    float(config_row["faithfulness"].iloc[0]), 4
                )
                row[f"{config}_relevance"] = round(
                    float(config_row["answer_relevancy"].iloc[0]), 4
                )
            else:
                row[f"{config}_faithfulness"] = float("nan")
                row[f"{config}_relevance"] = float("nan")

        pivot_rows.append(row)

    pivot_df = pd.DataFrame(pivot_rows)

    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)
    pivot_df.to_csv(RESULTS_CSV, index=False)
    logger.info(f"Results saved to: {RESULTS_CSV}")
    logger.info(f"\n{pivot_df.to_string(index=False)}")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    from production_rag.contextualizer import contextualize_corpus

    logger.info("Step 1: Indexing naive corpus.")
    index_naive_corpus()

    logger.info("Step 2: Indexing contextual corpus (this calls Groq API for each chunk).")
    contextualize_corpus()

    logger.info("Step 3: Running eval harness across all 4 configurations.")
    results_df = run_eval_harness()

    logger.info("Step 4: Saving pivoted results CSV.")
    save_results(results_df)
