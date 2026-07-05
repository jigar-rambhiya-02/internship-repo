"""
src/schema_loader.py

Responsibilities:
  1. Create and return an authenticated BigQuery client.
  2. Fetch the schema of a specified table.
  3. Format the schema into a prompt-friendly string, including sample values.

Design decisions:
  - BigQuery client creation uses Application Default Credentials (ADC).
    The GOOGLE_APPLICATION_CREDENTIALS env var (set in settings.py) points to
    the service account JSON key, which ADC picks up automatically.
  - Sample values are fetched with a LIMIT query per column. This gives the LLM
    concrete examples of what data looks like, dramatically reducing hallucinated
    column names (e.g., the LLM won't guess "pickup_date" if it sees "tpep_pickup_datetime").
  - Schema truncation: if the table has more columns than MAX_SCHEMA_COLUMNS,
    we prioritize by dropping columns whose names suggest they are low-value for
    SQL generation (e.g., internal IDs, surcharge breakdowns).
"""

import sys
from google.cloud import bigquery
from typing import Optional
from google.api_core.exceptions import GoogleAPIError
from config.settings import (
    PROJECT_ID,
    DATASET_ID,
    TABLE_ID,
    MAX_SCHEMA_COLUMNS,
    SAMPLE_VALUES_PER_COLUMN,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# BigQuery client factory — STRICT / FAIL-FAST
# ---------------------------------------------------------------------------

def get_bigquery_client() -> bigquery.Client:
    """
    Create and return a BigQuery Client using Application Default Credentials.

    Exits the process with code 1 if client creation fails — this is a fatal
    infrastructure error that cannot be recovered from gracefully.

    Returns:
        An authenticated bigquery.Client instance.
    """
    logger.info("Initializing BigQuery client...")
    try:
        client = bigquery.Client()
        logger.info("BigQuery client initialized successfully.")
        return client
    except Exception as exc:
        logger.critical(
            f"Failed to initialize BigQuery client. "
            f"Check GOOGLE_APPLICATION_CREDENTIALS. Error: {exc}"
        )
        sys.exit(1)


# Module-level singleton client — created once and reused across all calls.
# This avoids repeated ADC negotiation on every schema fetch.
# _bq_client: bigquery.Client | None = None ------------- this is the  line from the guide.md
_bq_client: Optional[bigquery.Client] = None   # by deepseek


def _get_client() -> bigquery.Client:
    """Return the module-level BigQuery client, creating it if necessary."""
    global _bq_client
    if _bq_client is None:
        _bq_client = get_bigquery_client()
    return _bq_client


# ---------------------------------------------------------------------------
# Schema fetching
# ---------------------------------------------------------------------------

def fetch_table_schema(dataset_id: str, table_id: str) -> bigquery.Table:
    """
    Fetch the BigQuery Table object, which contains the schema (field definitions).

    Args:
        dataset_id: BigQuery dataset name (e.g., "new_york_taxi_trips").
        table_id: Table name (e.g., "tlc_yellow_trips_2015").

    Returns:
        A bigquery.Table object with the full schema.

    Raises:
        SystemExit: If the table cannot be fetched (fail-fast behaviour).
    """
    client = _get_client()
    full_table_id = f"{PROJECT_ID}.{dataset_id}.{table_id}"
    logger.info(f"Fetching schema for table: {full_table_id}")
    try:
        table = client.get_table(full_table_id)
        logger.info(
            f"Schema fetched. Table has {len(table.schema)} columns, "
            f"approximately {table.num_rows:,} rows."
        )
        return table
    except GoogleAPIError as exc:
        logger.critical(
            f"Failed to fetch schema for {full_table_id}. "
            f"Check that the table exists and the service account has BigQuery Data Viewer role. "
            f"Error: {exc}"
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Sample value fetching
# ---------------------------------------------------------------------------

def _fetch_sample_values(
    dataset_id: str,
    table_id: str,
    column_name: str,
    n: int = SAMPLE_VALUES_PER_COLUMN,
) -> list[str]:
    """
    Fetch up to `n` distinct non-null sample values for a single column.
    Used to populate the schema prompt with concrete examples.

    Args:
        dataset_id: BigQuery dataset name.
        table_id: Table name.
        column_name: Column to sample.
        n: Number of distinct values to retrieve.

    Returns:
        A list of string representations of the sample values.
        Returns an empty list on failure (graceful — sampling is best-effort).
    """
    client = _get_client()
    full_ref = f"`{PROJECT_ID}.{dataset_id}.{table_id}`"
    # SAFE_CAST to STRING handles all column types (TIMESTAMP, FLOAT, etc.)
    sql = (
        f"SELECT DISTINCT SAFE_CAST(`{column_name}` AS STRING) AS val "
        f"FROM {full_ref} "
        f"WHERE `{column_name}` IS NOT NULL "
        f"LIMIT {n}"
    )
    try:
        rows = list(client.query(sql).result())
        return [str(row.val) for row in rows if row.val is not None]
    except Exception as exc:
        logger.warning(
            f"Could not fetch sample values for column '{column_name}': {exc}"
        )
        return []


# ---------------------------------------------------------------------------
# Schema → prompt string
# ---------------------------------------------------------------------------

def format_schema_for_prompt(
    dataset_id: str = DATASET_ID,
    table_id: str = TABLE_ID,
) -> str:
    """
    Build a human-readable schema string suitable for injection into an LLM prompt.

    Each column line looks like:
      - vendor_id (STRING, NULLABLE) — sample values: ['1', '2', 'CMT']

    If the table has more than MAX_SCHEMA_COLUMNS columns, the schema is truncated
    by dropping columns whose names suggest low analytical value (internal IDs,
    surcharge breakdowns). A truncation notice is appended so the LLM knows the
    schema is not exhaustive.

    Args:
        dataset_id: BigQuery dataset name.
        table_id: Table name.

    Returns:
        A formatted schema string ready to embed in a prompt.
    """
    table = fetch_table_schema(dataset_id, table_id)
    schema_fields = list(table.schema)

    # --- Truncation strategy ---
    if len(schema_fields) > MAX_SCHEMA_COLUMNS:
        logger.warning(
            f"Table has {len(schema_fields)} columns; truncating to {MAX_SCHEMA_COLUMNS} "
            f"for context window management."
        )
        # Heuristic: deprioritise columns with these substrings in their names
        low_priority_keywords = ["surcharge", "tax", "_id", "store_and", "improvement"]
        priority_fields = [
            f for f in schema_fields
            if not any(kw in f.name.lower() for kw in low_priority_keywords)
        ]
        # Fill remaining budget with the rest
        remaining = [f for f in schema_fields if f not in priority_fields]
        schema_fields = (priority_fields + remaining)[:MAX_SCHEMA_COLUMNS]

    full_table_ref = f"`{PROJECT_ID}.{dataset_id}.{table_id}`"
    lines = [
        f"Table: {full_table_ref}",
        f"Columns ({len(schema_fields)} shown):",
    ]

    for field in schema_fields:
        logger.debug(f"Fetching sample values for column: {field.name}")
        samples = _fetch_sample_values(dataset_id, table_id, field.name)
        sample_str = str(samples) if samples else "N/A"
        lines.append(
            f"  - {field.name} ({field.field_type}, {field.mode}) "
            f"— sample values: {sample_str}"
        )

    if len(table.schema) > MAX_SCHEMA_COLUMNS:
        lines.append(
            f"\n[NOTE: Schema truncated. Table has {len(table.schema)} total columns. "
            f"Use only the columns listed above.]"
        )

    schema_string = "\n".join(lines)
    logger.info(
        f"Schema formatted for prompt. Total characters: {len(schema_string)}"
    )
    return schema_string
