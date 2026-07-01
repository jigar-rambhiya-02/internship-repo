"""
tests/test_queries.py

Batch runner for the Text-to-SQL pipeline.

Defines 15 natural language queries across three difficulty tiers:
  - Easy (1-5): Single-table aggregations, simple filters, COUNT/AVG.
  - Medium (6-10): Multi-column grouping, date extraction, TOP-N, subqueries.
  - Hard (11-15): Window functions, CTEs, rolling averages, self-joins, RANK.

For each query, calls agent.run_pipeline() and logs the result.
At the end, prints a formatted summary report.

All artifacts are saved to test_results/query_{id}/ by the pipeline.
"""

import sys
import os

# Ensure the project root is on sys.path so imports resolve correctly
# when running `python tests/test_queries.py` from the text2sql/ directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import run_pipeline
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Query definitions — 15 NL questions across Easy / Medium / Hard
# ---------------------------------------------------------------------------

QUERIES = [
    # --- EASY (1-5) ---
    {
        "id": 1,
        "difficulty": "easy",
        "question": "How many yellow taxi trips were there in 2015?",
    },
    {
        "id": 2,
        "difficulty": "easy",
        "question": "What is the average trip distance for all yellow taxi trips?",
    },
    {
        "id": 3,
        "difficulty": "easy",
        "question": "What is the total fare amount collected across all yellow taxi trips in 2015?",
    },
    {
        "id": 4,
        "difficulty": "easy",
        "question": "How many trips had more than 4 passengers?",
    },
    {
        "id": 5,
        "difficulty": "easy",
        "question": "What is the maximum tip amount recorded in the dataset?",
    },
    # --- MEDIUM (6-10) ---
    {
        "id": 6,
        "difficulty": "medium",
        "question": (
            "Find the top 5 pickup location IDs by total fare amount "
            "in January 2015."
        ),
    },
    {
        "id": 7,
        "difficulty": "medium",
        "question": (
            "Compare the average trip distance grouped by passenger count. "
            "Show passenger count and average distance."
        ),
    },
    {
        "id": 8,
        "difficulty": "medium",
        "question": (
            "What is the total number of trips and average fare amount "
            "for each day of the week in 2015?"
        ),
    },
    {
        "id": 9,
        "difficulty": "medium",
        "question": (
            "Find the top 10 dropoff location IDs that generated the highest "
            "average tip percentage (tip_amount / fare_amount * 100) "
            "for trips with fare_amount > 5."
        ),
    },
    {
        "id": 10,
        "difficulty": "medium",
        "question": (
            "How many trips were there per month in 2015? "
            "Show the month number and trip count, ordered by month."
        ),
    },
    # --- HARD (11-15) ---
    {
        "id": 11,
        "difficulty": "hard",
        "question": (
            "Using a window function, rank each day in 2015 by total number of trips, "
            "from highest to lowest. Show the date and its rank."
        ),
    },
    {
        "id": 12,
        "difficulty": "hard",
        "question": (
            "Calculate the 7-day rolling average number of trips for each day "
            "in March 2015 using a CTE. Show the date and the rolling average."
        ),
    },
    {
        "id": 13,
        "difficulty": "hard",
        "question": (
            "For each pickup location ID, find the percentage of trips where "
            "the tip amount was greater than 20 percent of the fare amount. "
            "Only include locations with more than 100 trips. "
            "Show the top 10 locations by this percentage."
        ),
    },
    {
        "id": 14,
        "difficulty": "hard",
        "question": (
            "Using a CTE, calculate the average fare amount per hour of day "
            "(0-23) and identify the top 3 and bottom 3 hours by average fare. "
            "Return all hours with their average fare and a label "
            "('top', 'bottom', or 'middle')."
        ),
    },
    {
        "id": 15,
        "difficulty": "hard",
        "question": (
            "Using window functions, for each day in January 2015, calculate "
            "the cumulative total fare amount from the start of the month, "
            "and the percentage of the month's total fare each day represents. "
            "Order by date."
        ),
    },
]


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Run all 15 queries through the pipeline and print a summary report.

    The function does not exit early on individual query failures —
    all queries are attempted regardless of previous failures.
    """
    logger.info(
        f"=== Starting batch run. Total queries: {len(QUERIES)} ==="
    )

    results = []

    for query in QUERIES:
        query_id = query["id"]
        question = query["question"]
        difficulty = query["difficulty"]

        logger.info(
            f"--- Running query {query_id}/15 [{difficulty.upper()}]: {question} ---"
        )

        result = run_pipeline(question=question, query_id=query_id)
        result["difficulty"] = difficulty
        results.append(result)

        status_icon = "✅" if result["success"] else "❌"
        logger.info(
            f"Query {query_id} [{difficulty}]: {status_icon} "
            f"{'SUCCESS' if result['success'] else 'FAILED'}"
        )

    # ------------------------------------------------------------------
    # Summary report
    # ------------------------------------------------------------------
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]

    easy_results = [r for r in results if r["difficulty"] == "easy"]
    medium_results = [r for r in results if r["difficulty"] == "medium"]
    hard_results = [r for r in results if r["difficulty"] == "hard"]

    def pass_rate(subset: list) -> str:
        passed = sum(1 for r in subset if r["success"])
        return f"{passed}/{len(subset)}"

    report_lines = [
        "",
        "=" * 60,
        "  TEXT-TO-SQL PIPELINE — BATCH RUN SUMMARY",
        "=" * 60,
        f"  Total queries run : {len(results)}",
        f"  Successful        : {len(successes)}",
        f"  Failed            : {len(failures)}",
        f"  Overall pass rate : {len(successes)}/{len(results)} "
        f"({100 * len(successes) // len(results)}%)",
        "-" * 60,
        f"  Easy   pass rate  : {pass_rate(easy_results)}",
        f"  Medium pass rate  : {pass_rate(medium_results)}",
        f"  Hard   pass rate  : {pass_rate(hard_results)}",
        "-" * 60,
    ]

    if failures:
        report_lines.append("  Failed queries:")
        for r in failures:
            report_lines.append(
                f"    Query {r['query_id']:>2} [{r['difficulty']:6}]: "
                f"{r['question'][:60]}..."
            )
            report_lines.append(
                f"              Error: {r['error'][:80]}"
            )

    report_lines.append("=" * 60)
    report_lines.append("")

    report_str = "\n".join(report_lines)
    print(report_str)
    logger.info(f"Batch run complete.\n{report_str}")


if __name__ == "__main__":
    main()
