# eval/run_eval.py
import json
import os
import time
from pathlib import Path

import chromadb
import matplotlib.pyplot as plt
import pandas as pd
from groq import Groq
from tqdm import tqdm

from config import settings
from eval.judges import (
    judge_answer_relevance,
    judge_context_precision,
    judge_context_recall,
    judge_faithfulness,
)
from src.rag_bot import get_rag_response
from src.utils import load_jsonl, setup_logger

logger = setup_logger(__name__)


def load_test_set(path: str) -> list[dict]:
    logger.info(f"Loading test set from {path}")
    data = load_jsonl(path)
    logger.info(f"Loaded {len(data)} questions from {path}")
    return data


def run_single_evaluation(item: dict, collection, client) -> dict:
    question_id = item["question_id"]
    question = item["question"]
    ground_truth_answer = item["ground_truth_answer"]
    ground_truth_chunk_ids = item["ground_truth_chunk_ids"]

    logger.info(f"Evaluating {question_id}: {question[:80]}...")

    rag_result = get_rag_response(question, collection, client)
    answer = rag_result["answer"]
    retrieved_chunks = rag_result["retrieved_chunks"]
    retrieved_chunk_ids = rag_result["retrieved_chunk_ids"]

    faithfulness = judge_faithfulness(
        question,
        answer,
        retrieved_chunks,
        ground_truth_answer,
        ground_truth_chunk_ids,
        retrieved_chunk_ids,
        client,
    )
    answer_relevance = judge_answer_relevance(
        question,
        answer,
        retrieved_chunks,
        ground_truth_answer,
        ground_truth_chunk_ids,
        retrieved_chunk_ids,
        client,
    )
    context_precision = judge_context_precision(
        question,
        answer,
        retrieved_chunks,
        ground_truth_answer,
        ground_truth_chunk_ids,
        retrieved_chunk_ids,
        client,
    )
    context_recall = judge_context_recall(
        question,
        answer,
        retrieved_chunks,
        ground_truth_answer,
        ground_truth_chunk_ids,
        retrieved_chunk_ids,
        client,
    )

    scores = [
        faithfulness["score"],
        answer_relevance["score"],
        context_precision["score"],
        context_recall["score"],
    ]
    valid_scores = [s for s in scores if s is not None]
    avg_score = (
        round(sum(valid_scores) / len(valid_scores), 4) if valid_scores else None
    )

    result = {
        "question_id": question_id,
        "question": question,
        "answer": answer,
        "retrieved_chunk_ids": json.dumps(retrieved_chunk_ids),
        "faithfulness_score": faithfulness["score"],
        "faithfulness_reasoning": faithfulness["reasoning"],
        "answer_relevance_score": answer_relevance["score"],
        "answer_relevance_reasoning": answer_relevance["reasoning"],
        "context_precision_score": context_precision["score"],
        "context_precision_reasoning": context_precision["reasoning"],
        "context_recall_score": context_recall["score"],
        "context_recall_reasoning": context_recall["reasoning"],
        "avg_score": avg_score,
    }

    return result


def save_results_csv(results: list[dict], path: str) -> None:
    df = pd.DataFrame(results)
    score_cols = [
        "faithfulness_score",
        "answer_relevance_score",
        "context_precision_score",
        "context_recall_score",
        "avg_score",
    ]
    for col in score_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: round(x, 4) if pd.notna(x) and x is not None else x
            )

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info(f"Saved results CSV to {path} ({len(df)} rows)")


def _df_to_markdown(df: pd.DataFrame) -> str:
    lines = []
    headers = "| " + " | ".join(df.columns) + " |"
    separators = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    lines.append(headers)
    lines.append(separators)
    for _, row in df.iterrows():
        row_str = (
            "| "
            + " | ".join(str(v) if v is not None else "N/A" for v in row.values)
            + " |"
        )
        lines.append(row_str)
    return "\n".join(lines)


def generate_eval_report(results_df: pd.DataFrame, output_path: str) -> None:
    logger.info("Generating evaluation report...")

    score_cols = [
        "faithfulness_score",
        "answer_relevance_score",
        "context_precision_score",
        "context_recall_score",
    ]

    stats = []
    for col in score_cols:
        valid = results_df[col].dropna()
        stats.append(
            {
                "Metric": col.replace("_score", "").replace("_", " ").title(),
                "Mean": round(valid.mean(), 4) if len(valid) > 0 else None,
                "Min": round(valid.min(), 4) if len(valid) > 0 else None,
                "Max": round(valid.max(), 4) if len(valid) > 0 else None,
                "Std Dev": round(valid.std(), 4) if len(valid) > 0 else None,
                "Valid Count": len(valid),
            }
        )
    stats_df = pd.DataFrame(stats)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    colors = ["#2ecc71", "#3498db", "#e74c3c", "#f39c12"]

    for idx, col in enumerate(score_cols):
        ax = axes[idx]
        valid = results_df[col].dropna()
        if len(valid) > 0:
            ax.hist(
                valid,
                bins=10,
                range=(0, 1),
                color=colors[idx],
                edgecolor="black",
                alpha=0.7,
            )
            ax.set_title(col.replace("_score", "").replace("_", " ").title())
            ax.set_xlabel("Score")
            ax.set_ylabel("Frequency")
            ax.set_xlim(0, 1)
        else:
            ax.text(
                0.5,
                0.5,
                "No valid scores",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_title(col.replace("_score", "").replace("_", " ").title())

    plt.tight_layout()
    hist_path = Path(output_path).parent / "score_distribution.png"
    plt.savefig(hist_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved histogram to {hist_path}")

    if results_df["avg_score"].notna().sum() == 0:
        logger.warning("No valid average scores; best/worst case selection may be arbitrary.")
        top3 = results_df.head(3)
        bottom3 = results_df.tail(3)
    else:
        top3 = results_df.sort_values("avg_score", ascending=False, na_position="last").head(3)
        bottom3 = results_df.sort_values("avg_score", ascending=True, na_position="first").head(3)

    lines = []
    lines.append("# RAG Evaluation Report")
    lines.append(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"\nTotal Questions Evaluated: {len(results_df)}")
    lines.append("\n---\n")

    lines.append("## Aggregate Metrics\n")
    lines.append(_df_to_markdown(stats_df))
    lines.append("\n")

    lines.append("## Score Distribution\n")
    lines.append("![Score Distribution](score_distribution.png)")
    lines.append("\n")

    lines.append("## Top 3 Best Answers (by Average Score)\n")
    for _, row in top3.iterrows():
        lines.append(f"### {row['question_id']}: {row['question']}\n")
        lines.append(f"**Answer:** {row['answer']}\n")
        lines.append(f"**Retrieved Chunks:** {row['retrieved_chunk_ids']}\n")
        lines.append(f"**Avg Score:** {row['avg_score']}\n")
        lines.append(
            f"- **Faithfulness ({row['faithfulness_score']}):** {row['faithfulness_reasoning']}\n"
        )
        lines.append(
            f"- **Answer Relevance ({row['answer_relevance_score']}):** {row['answer_relevance_reasoning']}\n"
        )
        lines.append(
            f"- **Context Precision ({row['context_precision_score']}):** {row['context_precision_reasoning']}\n"
        )
        lines.append(
            f"- **Context Recall ({row['context_recall_score']}):** {row['context_recall_reasoning']}\n"
        )
        lines.append("\n---\n")

    lines.append("## Bottom 3 Worst Answers (by Average Score)\n")
    for _, row in bottom3.iterrows():
        lines.append(f"### {row['question_id']}: {row['question']}\n")
        lines.append(f"**Answer:** {row['answer']}\n")
        lines.append(f"**Retrieved Chunks:** {row['retrieved_chunk_ids']}\n")
        lines.append(f"**Avg Score:** {row['avg_score']}\n")
        lines.append(
            f"- **Faithfulness ({row['faithfulness_score']}):** {row['faithfulness_reasoning']}\n"
        )
        lines.append(
            f"- **Answer Relevance ({row['answer_relevance_score']}):** {row['answer_relevance_reasoning']}\n"
        )
        lines.append(
            f"- **Context Precision ({row['context_precision_score']}):** {row['context_precision_reasoning']}\n"
        )
        lines.append(
            f"- **Context Recall ({row['context_recall_score']}):** {row['context_recall_reasoning']}\n"
        )

        metric_scores = {
            "Faithfulness": row["faithfulness_score"],
            "Answer Relevance": row["answer_relevance_score"],
            "Context Precision": row["context_precision_score"],
            "Context Recall": row["context_recall_score"],
        }
        valid_metrics = {k: v for k, v in metric_scores.items() if v is not None}
        if valid_metrics:
            lowest_metric = min(valid_metrics, key=valid_metrics.get)
            lowest_score = valid_metrics[lowest_metric]
            lines.append(
                f"\n**Root Cause Analysis:** The lowest score was **{lowest_metric}** ({lowest_score}). "
            )
            if lowest_metric == "Faithfulness":
                lines.append(
                    "The answer likely hallucinated or contradicted the retrieved context. Review the chunking strategy and ensure the generator prompt strictly grounds the model.\n"
                )
            elif lowest_metric == "Answer Relevance":
                lines.append(
                    "The answer failed to address the actual question. The retrieval may have fetched off-topic chunks, or the generator may have misinterpreted the question.\n"
                )
            elif lowest_metric == "Context Precision":
                lines.append(
                    "The retriever returned noisy or irrelevant chunks. Consider tuning the embedding model, adjusting top_k, or filtering chunks by similarity threshold.\n"
                )
            elif lowest_metric == "Context Recall":
                lines.append(
                    "The retriever missed critical chunks needed to answer the question. The corpus may lack coverage, or the embedding similarity search failed to surface the correct chunks.\n"
                )
        lines.append("\n---\n")

    lines.append("## Prioritized Improvement Roadmap\n")
    lines.append(
        "Based on aggregate metric scores, ranked from lowest-performing to highest:\n"
    )
    metric_means = {
        "Faithfulness": stats_df[stats_df["Metric"] == "Faithfulness"]["Mean"].values[0],
        "Answer Relevance": stats_df[stats_df["Metric"] == "Answer Relevance"]["Mean"].values[0],
        "Context Precision": stats_df[stats_df["Metric"] == "Context Precision"]["Mean"].values[0],
        "Context Recall": stats_df[stats_df["Metric"] == "Context Recall"]["Mean"].values[0],
    }
    sorted_metrics = sorted(
        [(k, v) for k, v in metric_means.items() if v is not None],
        key=lambda x: x[1],
    )

    for rank, (metric, mean) in enumerate(sorted_metrics, 1):
        lines.append(f"{rank}. **{metric}** (Mean: {mean}) — ")
        if metric == "Faithfulness":
            lines.append(
                "Strengthen the generator system prompt with stricter grounding instructions. Add a post-generation fact-checking layer against retrieved chunks.\n"
            )
        elif metric == "Answer Relevance":
            lines.append(
                "Improve query understanding by adding query rewriting or expansion. Ensure the generator is explicitly instructed to answer the exact question asked.\n"
            )
        elif metric == "Context Precision":
            lines.append(
                "Implement a similarity threshold filter to drop low-relevance chunks. Consider re-ranking retrieved chunks with a cross-encoder before passing to the generator.\n"
            )
        elif metric == "Context Recall":
            lines.append(
                "Increase top_k or implement hybrid search (dense + keyword). Audit the corpus for coverage gaps and add missing documents.\n"
            )

    report_text = "\n".join(lines)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    logger.info(f"Saved evaluation report to {output_path}")


def main():
    logger.info("=== Evaluation Pipeline Started ===")
    start_time = time.time()

    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY not found in environment")
        raise ValueError("GROQ_API_KEY not found")

    client = Groq(api_key=api_key)

    chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    collection = chroma_client.get_or_create_collection(name="rag_corpus")

    test_set = load_test_set(settings.EVAL_TEST_SET_PATH)

    results = []
    full_success = 0
    partial_failure = 0

    for item in tqdm(test_set, desc="Evaluating"):
        try:
            result = run_single_evaluation(item, collection, client)
            results.append(result)

            scores = [
                result["faithfulness_score"],
                result["answer_relevance_score"],
                result["context_precision_score"],
                result["context_recall_score"],
            ]
            if all(s is not None for s in scores):
                full_success += 1
            else:
                partial_failure += 1
        except Exception as e:
            logger.error(
                f"Fatal error evaluating {item.get('question_id', 'UNKNOWN')}: {e}",
                exc_info=True,
            )
            partial_failure += 1
            continue

    save_results_csv(results, settings.EVAL_RESULTS_PATH)
    results_df = pd.DataFrame(results)
    generate_eval_report(results_df, "eval/eval_report.md")

    elapsed = time.time() - start_time
    logger.info(
        f"=== Evaluation Pipeline Completed in {elapsed:.2f}s ==="
    )
    logger.info(
        f"Summary: {full_success}/{len(test_set)} questions fully scored, {partial_failure} had partial failures"
    )


if __name__ == "__main__":
    main()
