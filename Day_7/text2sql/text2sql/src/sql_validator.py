"""
src/sql_validator.py

Responsibilities:
  1. dry_run_query: Use BigQuery's dry-run mode to validate SQL without executing it.
  2. retry_sql_generation: Build a correction prompt and call Groq to produce
     a fixed SQL statement after a dry-run failure.

BigQuery dry-run acts as a compile-time check:
  - It parses the SQL and resolves all column/table references against the actual schema.
  - It returns the estimated bytes scanned (useful for cost control).
  - It raises google.api_core.exceptions.BadRequest with a structured error message
    if the SQL is invalid. That exact error message is injected back into the retry prompt.

Design decision — why inject the raw BigQuery error?
  LLMs respond much better to correction prompts that include the actual error
  (e.g., "Unrecognized name: pickup_date; Did you mean tpep_pickup_datetime?")
  than to vague instructions like "the SQL was invalid, try again".
"""

import groq as groq_sdk
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest

from config.settings import (
    GROQ_API_KEY,
    GROQ_MODEL,
    SQL_TEMPERATURE,
    MAX_TOKENS,
)
from src.utils.logger import get_logger
from src.schema_loader import _get_client  # reuse module-level BQ client

logger = get_logger(__name__)

# Groq client — module-level singleton
_groq_client = groq_sdk.Groq(api_key=GROQ_API_KEY)


# ---------------------------------------------------------------------------
# Dry-run validation
# ---------------------------------------------------------------------------

def dry_run_query(sql: str) -> tuple[bool, str]:
    """
    Submit a SQL query to BigQuery in dry-run mode.

    Dry-run mode parses and validates the SQL against the real schema without
    actually scanning any data. Cost: $0.00 per dry run.

    Args:
        sql: The SQL string to validate.

    Returns:
        (True, "") if the SQL is valid.
        (False, error_message) if BigQuery rejects the SQL.
    """
    client = _get_client()
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)

    logger.info(f"Running BigQuery dry-run validation. SQL length: {len(sql)} chars.")
    logger.debug(f"SQL to validate:\n{sql}")

    try:
        # A dry-run job returns immediately without executing the query.
        # If the SQL is valid, job.total_bytes_processed contains the estimate.
        job = client.query(sql, job_config=job_config)
        estimated_bytes = job.total_bytes_processed
        logger.info(
            f"Dry-run PASSED. Estimated bytes to scan: "
            f"{estimated_bytes / 1e6:.2f} MB"
        )
        return True, ""
    except BadRequest as exc:
        # BigQuery returns a structured error — extract the human-readable message.
        error_message = str(exc)
        logger.warning(f"Dry-run FAILED. BigQuery error: {error_message}")
        return False, error_message
    except Exception as exc:
        # Catch unexpected errors (network issues, quota exceeded, etc.)
        error_message = f"Unexpected dry-run error: {exc}"
        logger.error(error_message)
        return False, error_message


# ---------------------------------------------------------------------------
# SQL retry via Groq
# ---------------------------------------------------------------------------

def retry_sql_generation(
    nl_question: str,
    schema: str,
    failed_sql: str,
    error_msg: str,
    attempt: int,
) -> str:
    """
    Build a correction prompt and ask Groq to produce a fixed SQL statement.

    The correction prompt explicitly includes:
      - The original natural language question (so the LLM remembers the intent)
      - The table schema (so it can reference correct column names)
      - The SQL that failed (so it understands what was wrong)
      - The exact BigQuery error message (the most actionable correction signal)

    Args:
        nl_question: The original user question.
        schema: The formatted schema string from format_schema_for_prompt().
        failed_sql: The SQL statement that failed the dry-run.
        error_msg: The error message returned by BigQuery.
        attempt: The current retry attempt number (1 or 2), used for logging.

    Returns:
        A new SQL string (stripped of markdown fences).
    """
    logger.info(
        f"Retrying SQL generation. Attempt {attempt} of 2. "
        f"Injecting BigQuery error into correction prompt."
    )

    # Construct a correction prompt using chain-of-thought style:
    # 1. Restate the goal.
    # 2. Show what went wrong.
    # 3. Ask for a correction.
    system_prompt = (
        "You are an expert BigQuery SQL engineer. "
        "You previously generated a SQL query that failed BigQuery validation. "
        "Your task is to correct the SQL based on the error message provided. "
        "Return ONLY the corrected raw SQL query. "
        "Do NOT wrap it in markdown code fences. "
        "Do NOT include any explanation. "
        "Use only the exact column names listed in the schema."
    )

    user_prompt = (
        f"Original question: {nl_question}\n\n"
        f"Schema:\n{schema}\n\n"
        f"Previous (invalid) SQL:\n{failed_sql}\n\n"
        f"BigQuery error message:\n{error_msg}\n\n"
        f"Please provide the corrected SQL query."
    )

    logger.info(
        f"Sending retry prompt to Groq. Model: {GROQ_MODEL}. "
        f"Prompt length (approx chars): {len(system_prompt) + len(user_prompt)}"
    )

    try:
        response = _groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=SQL_TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )

        corrected_sql = response.choices[0].message.content.strip()
        finish_reason = response.choices[0].finish_reason
        usage = response.usage

        logger.info(
            f"Groq retry response received. "
            f"Tokens used — prompt: {usage.prompt_tokens}, "
            f"completion: {usage.completion_tokens}. "
            f"Finish reason: {finish_reason}"
        )

        # Strip markdown fences if the model added them despite instructions
        corrected_sql = _strip_sql_fences(corrected_sql)
        logger.info(f"Corrected SQL (attempt {attempt}):\n{corrected_sql}")
        return corrected_sql

    except Exception as exc:
        logger.error(f"Groq API call failed during SQL retry: {exc}")
        # Return the original failed SQL so the caller can handle the failure
        return failed_sql


def _strip_sql_fences(text: str) -> str:
    """
    Remove markdown code fences from a SQL string.

    Models sometimes wrap SQL in ```sql ... ``` despite being instructed not to.
    This function handles both ```sql and ``` fences.

    Args:
        text: Raw LLM output.

    Returns:
        Clean SQL string with no markdown wrapping.
    """
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```sql or ```) and last line (```)
        if lines[-1].strip() == "```":
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        text = "\n".join(lines).strip()
    return text
