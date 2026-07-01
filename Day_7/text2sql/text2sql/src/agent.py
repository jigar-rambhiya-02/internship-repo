"""
src/agent.py

The orchestrator of the Text-to-SQL pipeline.

Responsibilities:
  1. build_sql_generation_prompt: Compose the system + user prompt for SQL generation.
  2. generate_sql: Call Groq and parse the raw SQL from the response.
  3. execute_query: Run validated SQL on BigQuery and return a DataFrame.
  4. run_pipeline: End-to-end orchestration for a single NL question.

The run_pipeline function follows this sequence:
  1. Fetch and format schema.
  2. Generate SQL via Groq.
  3. Dry-run validate. On failure, retry up to MAX_SQL_RETRIES times.
  4. Execute the validated SQL.
  5. Summarize results.
  6. Pick a chart type and render PNG.
  7. Save all artifacts to test_results/query_{query_id}/.
  8. Return a status dictionary for the batch runner.
"""

import os
import sys
import pandas as pd
import groq as groq_sdk
from typing import Optional
from google.cloud import bigquery

from config.settings import (
    GROQ_API_KEY,
    GROQ_MODEL,
    SQL_TEMPERATURE,
    MAX_TOKENS,
    MAX_SQL_RETRIES,
    TEST_RESULTS_DIR,
    PROJECT_ID,
    DATASET_ID,
    TABLE_ID,
)
from src.utils.logger import get_logger
from src.schema_loader import format_schema_for_prompt, _get_client
from src.sql_validator import dry_run_query, retry_sql_generation, _strip_sql_fences
from src.summarizer import summarize
from src.chart_picker import pick_chart, render_chart

logger = get_logger(__name__)

# Groq client — module-level singleton
_groq_client = groq_sdk.Groq(api_key=GROQ_API_KEY)


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def build_sql_generation_prompt(question: str, schema: str) -> tuple[str, str]:
    """
    Build the system prompt and user prompt for SQL generation.

    Design choices in the prompt:
      - The system prompt establishes the model's role and hard constraints
        (use only listed columns, no markdown fences, BigQuery dialect).
      - The user prompt provides the schema and the specific question.
      - Temperature is kept at 0.1 so the model prefers the most statistically
        common (correct) SQL patterns over creative/hallucinated ones.
      - Explicit instruction "use only the columns listed" is the single most
        effective technique for preventing column name hallucination.

    Args:
        question: The natural language question from the user.
        schema: The formatted schema string from format_schema_for_prompt().

    Returns:
        A tuple of (system_prompt, user_prompt).
    """
    system_prompt = (
        "You are an expert BigQuery SQL engineer with deep knowledge of the "
        "Google Cloud BigQuery dialect. Your only job is to write a single, "
        "valid BigQuery SQL query that answers the user's question.\n\n"
        "STRICT RULES:\n"
        "1. Use ONLY the column names and table name provided in the schema below.\n"
        "2. Do NOT invent column names that are not in the schema.\n"
        "3. Use standard BigQuery SQL syntax (backtick-quoted identifiers, "
        "TIMESTAMP functions, EXTRACT, etc.).\n"
        "4. Return ONLY the raw SQL query — no markdown code fences, "
        "no explanations, no comments.\n"
        "5. Ensure the query is complete and executable as-is.\n"
        "6. For aggregation queries, always include a LIMIT clause (e.g., LIMIT 100) "
        "to prevent accidentally scanning billions of rows.\n"
        "7. For date/time filtering, use BigQuery TIMESTAMP or DATE functions correctly."
    )

    user_prompt = (
        f"Schema:\n{schema}\n\n"
        f"Question: {question}\n\n"
        f"Write the BigQuery SQL query:"
    )

    return system_prompt, user_prompt


# ---------------------------------------------------------------------------
# SQL generation via Groq
# ---------------------------------------------------------------------------

def generate_sql(system_prompt: str, user_prompt: str) -> str:
    """
    Call the Groq API to generate a SQL query.

    Logs:
      - Approximate prompt token count (character count / 4 as heuristic)
      - Model used
      - Response token counts and finish reason

    Args:
        system_prompt: The system-role prompt string.
        user_prompt: The user-role prompt string.

    Returns:
        A SQL string with markdown fences stripped.

    Raises:
        RuntimeError: If the Groq API call fails after internal retries.
    """
    approx_prompt_tokens = (len(system_prompt) + len(user_prompt)) // 4
    logger.info(
        f"Calling Groq API for SQL generation. "
        f"Model: {GROQ_MODEL}. "
        f"Approx prompt tokens: {approx_prompt_tokens}."
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

        raw_sql = response.choices[0].message.content.strip()
        finish_reason = response.choices[0].finish_reason
        usage = response.usage

        logger.info(
            f"Groq SQL generation complete. "
            f"Prompt tokens: {usage.prompt_tokens}. "
            f"Completion tokens: {usage.completion_tokens}. "
            f"Finish reason: {finish_reason}."
        )

        # Strip markdown fences defensively even though we instructed the model
        # not to include them — models occasionally disobey.
        sql = _strip_sql_fences(raw_sql)
        logger.info(f"Generated SQL:\n{sql}")
        return sql

    except groq_sdk.APIConnectionError as exc:
        raise RuntimeError(f"Groq API connection error: {exc}") from exc
    except groq_sdk.RateLimitError as exc:
        raise RuntimeError(f"Groq API rate limit exceeded: {exc}") from exc
    except groq_sdk.APIStatusError as exc:
        raise RuntimeError(
            f"Groq API status error {exc.status_code}: {exc.message}"
        ) from exc


# ---------------------------------------------------------------------------
# BigQuery query execution
# ---------------------------------------------------------------------------

def execute_query(sql: str) -> pd.DataFrame:
    """
    Execute a validated SQL query against BigQuery and return the result as a DataFrame.

    Args:
        sql: A BigQuery SQL string that has already passed dry-run validation.

    Returns:
        A pandas DataFrame containing the query results.

    Raises:
        RuntimeError: If query execution fails.
    """
    client = _get_client()
    logger.info(f"Executing BigQuery query. SQL length: {len(sql)} chars.")

    try:
        query_job = client.query(sql)
        df = query_job.to_dataframe()
        logger.info(
            f"Query execution complete. "
            f"Rows returned: {len(df)}. "
            f"Columns: {list(df.columns)}."
        )
        return df
    except Exception as exc:
        raise RuntimeError(f"BigQuery query execution failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Artifact saving
# ---------------------------------------------------------------------------

def _save_artifacts(
    query_id: int,
    nl_question: str,
    sql: str,
    validation_status: str,
    df: Optional[pd.DataFrame], 
    summary: str,
    chart_path: Optional[str],
    success: bool,
    error: str = "",
) -> str:
    """
    Save all pipeline artifacts for a single query to test_results/query_{query_id}/.

    Creates the directory if it does not exist.

    Returns:
        The path to the artifact directory.
    """
    artifact_dir = os.path.join(TEST_RESULTS_DIR, f"query_{query_id}")
    os.makedirs(artifact_dir, exist_ok=True)
    logger.info(f"Saving artifacts to: {artifact_dir}")

    # 1. Natural language question
    with open(os.path.join(artifact_dir, "nl_question.txt"), "w") as f:
        f.write(nl_question)

    # 2. Generated SQL
    with open(os.path.join(artifact_dir, "generated_sql.sql"), "w") as f:
        f.write(sql)

    # 3. Validation status
    with open(os.path.join(artifact_dir, "validation_status.txt"), "w") as f:
        f.write(validation_status)

    # 4. Result table as CSV
    if df is not None and not df.empty:
        df.to_csv(os.path.join(artifact_dir, "result_table.csv"), index=False)
    else:
        with open(os.path.join(artifact_dir, "result_table.csv"), "w") as f:
            f.write("(empty result)\n")

    # 5. NL summary
    with open(os.path.join(artifact_dir, "nl_summary.txt"), "w") as f:
        f.write(summary)

    # 6. Chart PNG — if chart was generated, it was already saved to chart_path
    # Copy the chart to the artifact directory if it's not already there
    if chart_path and os.path.exists(chart_path):
        target = os.path.join(artifact_dir, "chart.png")
        if os.path.abspath(chart_path) != os.path.abspath(target):
            import shutil
            shutil.copy2(chart_path, target)

    # 7. Success or failure marker
    if success:
        with open(os.path.join(artifact_dir, "success.txt"), "w") as f:
            f.write("Pipeline completed successfully.\n")
    else:
        with open(os.path.join(artifact_dir, "failure.txt"), "w") as f:
            f.write(f"Pipeline failed.\nError: {error}\n")

    logger.info(f"All artifacts saved for query_{query_id}.")
    return artifact_dir


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(question: str, query_id: int) -> dict:
    """
    Execute the full Text-to-SQL pipeline for a single natural language question.

    Steps:
      1. Fetch and format the BigQuery table schema.
      2. Build SQL generation prompt.
      3. Call Groq to generate SQL.
      4. Dry-run validate the SQL in BigQuery.
         - On failure, retry up to MAX_SQL_RETRIES times with error injection.
         - If all retries fail, return a graceful error dict.
      5. Execute the validated SQL and retrieve a DataFrame.
      6. Summarize the results using Groq.
      7. Pick a chart type and render a PNG.
      8. Save all artifacts to test_results/query_{query_id}/.
      9. Return a status dict for the batch runner.

    Args:
        question: The natural language question to answer.
        query_id: An integer identifier used to name the artifact directory.

    Returns:
        A dict with keys: query_id, question, success (bool), error (str),
        sql, summary, artifact_dir.
    """
    logger.info(
        f"=== Starting pipeline for query_id={query_id} === "
        f"Question: '{question}'"
    )

    # ------------------------------------------------------------------
    # Step 1: Schema loading — STRICT (exits on failure via schema_loader)
    # ------------------------------------------------------------------
    schema = format_schema_for_prompt(DATASET_ID, TABLE_ID)

    # ------------------------------------------------------------------
    # Step 2 & 3: Prompt construction and SQL generation
    # ------------------------------------------------------------------
    system_prompt, user_prompt = build_sql_generation_prompt(question, schema)
    try:
        sql = generate_sql(system_prompt, user_prompt)
    except RuntimeError as exc:
        error_msg = f"SQL generation failed: {exc}"
        logger.error(error_msg)
        _save_artifacts(
            query_id, question, "", "GENERATION_FAILED", None,
            error_msg, None, False, error_msg
        )
        return {
            "query_id": query_id, "question": question,
            "success": False, "error": error_msg,
            "sql": "", "summary": "", "artifact_dir": "",
        }

    # ------------------------------------------------------------------
    # Step 4: Dry-run validation with retry loop — LENIENT
    # ------------------------------------------------------------------
    current_sql = sql
    validation_passed = False
    last_error = ""

    for attempt in range(MAX_SQL_RETRIES + 1):  # attempt 0, 1, 2 = 3 total tries
        valid, bq_error = dry_run_query(current_sql)

        if valid:
            validation_passed = True
            logger.info(f"SQL passed dry-run validation on attempt {attempt + 1}.")
            break
        else:
            last_error = bq_error
            if attempt < MAX_SQL_RETRIES:
                logger.warning(
                    f"Dry-run failed on attempt {attempt + 1}. "
                    f"Retrying SQL generation ({attempt + 1}/{MAX_SQL_RETRIES})."
                )
                current_sql = retry_sql_generation(
                    nl_question=question,
                    schema=schema,
                    failed_sql=current_sql,
                    error_msg=bq_error,
                    attempt=attempt + 1,
                )
            else:
                logger.error(
                    f"SQL validation failed after {MAX_SQL_RETRIES + 1} total attempts."
                )

    if not validation_passed:
        graceful_message = (
            f"I was unable to generate valid SQL for this question after "
            f"{MAX_SQL_RETRIES + 1} attempts. Error: {last_error}"
        )
        logger.error(graceful_message)
        _save_artifacts(
            query_id, question, current_sql,
            f"FAILED: {last_error}", None,
            graceful_message, None, False, graceful_message
        )
        return {
            "query_id": query_id, "question": question,
            "success": False, "error": graceful_message,
            "sql": current_sql, "summary": graceful_message,
            "artifact_dir": os.path.join(TEST_RESULTS_DIR, f"query_{query_id}"),
        }

    # ------------------------------------------------------------------
    # Step 5: Execute validated SQL
    # ------------------------------------------------------------------
    try:
        df = execute_query(current_sql)
    except RuntimeError as exc:
        error_msg = str(exc)
        logger.error(f"Query execution failed: {error_msg}")
        _save_artifacts(
            query_id, question, current_sql,
            "PASSED_DRY_RUN_BUT_EXECUTION_FAILED", None,
            error_msg, None, False, error_msg
        )
        return {
            "query_id": query_id, "question": question,
            "success": False, "error": error_msg,
            "sql": current_sql, "summary": "", "artifact_dir": "",
        }

    # ------------------------------------------------------------------
    # Step 6: Summarize
    # ------------------------------------------------------------------
    summary = summarize(current_sql, df)

    # ------------------------------------------------------------------
    # Step 7: Chart selection and rendering
    # ------------------------------------------------------------------
    chart_type = pick_chart(df)
    chart_path = os.path.join(TEST_RESULTS_DIR, f"query_{query_id}", "chart.png")
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    render_chart(df, chart_type, chart_path)

    # ------------------------------------------------------------------
    # Step 8: Save artifacts
    # ------------------------------------------------------------------
    artifact_dir = _save_artifacts(
        query_id=query_id,
        nl_question=question,
        sql=current_sql,
        validation_status="PASSED",
        df=df,
        summary=summary,
        chart_path=chart_path,
        success=True,
    )

    logger.info(
        f"=== Pipeline complete for query_id={query_id}. "
        f"Artifacts at: {artifact_dir} ==="
    )

    return {
        "query_id": query_id,
        "question": question,
        "success": True,
        "error": "",
        "sql": current_sql,
        "summary": summary,
        "artifact_dir": artifact_dir,
    }
