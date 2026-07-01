"""
src/summarizer.py

Generates a concise natural-language summary of a BigQuery query result
using the Groq API.

Design decisions:
  - We send only the first 10 rows of the DataFrame as CSV text.
    Sending the full result (potentially thousands of rows) would:
      a) Exceed the context window for large results.
      b) Not improve summary quality — the LLM derives insight from patterns,
         not from memorising every row.
  - We include the SQL alongside the data so the LLM understands what the
    query was measuring, not just what numbers appeared in the result.
  - The summary is intentionally limited to 2-3 sentences — concise summaries
    are more useful in a BI dashboard context than verbose explanations.
"""

import pandas as pd
import groq as groq_sdk

from config.settings import (
    GROQ_API_KEY,
    GROQ_MODEL,
    SUMMARIZE_TEMPERATURE,
    MAX_TOKENS,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Groq client — module-level singleton
_groq_client = groq_sdk.Groq(api_key=GROQ_API_KEY)

# Maximum number of rows to include in the summarization prompt
MAX_ROWS_FOR_SUMMARY = 10


def summarize(sql: str, df: pd.DataFrame) -> str:
    """
    Generate a 2-3 sentence natural language summary of query results.

    Args:
        sql: The SQL query that was executed (included for context).
        df: The pandas DataFrame containing the query result.

    Returns:
        A plain English summary string. Returns a fallback message if the
        Groq API call fails.
    """
    if df.empty:
        logger.info("DataFrame is empty; returning no-data summary.")
        return "The query returned no results for the given conditions."

    # Truncate to the first MAX_ROWS_FOR_SUMMARY rows for the prompt
    preview_df = df.head(MAX_ROWS_FOR_SUMMARY)
    csv_preview = preview_df.to_csv(index=False)

    # Report truncation in the prompt so the LLM doesn't over-generalise
    truncation_note = ""
    if len(df) > MAX_ROWS_FOR_SUMMARY:
        truncation_note = (
            f"\n(Note: The full result has {len(df)} rows. "
            f"Only the first {MAX_ROWS_FOR_SUMMARY} are shown above.)"
        )

    system_prompt = (
        "You are a concise data analyst. You will be given a SQL query and "
        "a preview of its result. Write a 2-3 sentence natural language summary "
        "that explains what the data shows. Focus on the most interesting or "
        "actionable insight. Do not repeat column names verbatim; describe what "
        "they represent. Do not say 'the query shows' — just state the findings."
    )

    user_prompt = (
        f"SQL Query:\n{sql}\n\n"
        f"Result Preview (CSV):\n{csv_preview}{truncation_note}\n\n"
        f"Write a 2-3 sentence summary:"
    )

    logger.info(
        f"Calling Groq API for summarization. "
        f"Model: {GROQ_MODEL}. "
        f"DataFrame rows: {len(df)}, preview rows: {len(preview_df)}."
    )

    try:
        response = _groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=SUMMARIZE_TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )

        summary = response.choices[0].message.content.strip()
        usage = response.usage

        logger.info(
            f"Summarization complete. "
            f"Prompt tokens: {usage.prompt_tokens}. "
            f"Completion tokens: {usage.completion_tokens}."
        )
        logger.info(f"Summary: {summary}")
        return summary

    except Exception as exc:
        fallback = f"(Summary generation failed: {exc})"
        logger.error(f"Groq summarization API call failed: {exc}")
        return fallback
