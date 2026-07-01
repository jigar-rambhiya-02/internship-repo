"""
config/settings.py

Loads all environment variables and defines project-wide constants.
Uses STRICT / FAIL-FAST error handling: if required env vars are missing,
the process logs a critical error and exits immediately (sys.exit(1)).
This prevents silent failures where the pipeline runs but uses wrong credentials.
"""

import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Bootstrap a minimal logger for the settings module itself.
# The full dual-sink logger (src/utils/logger.py) is configured later,
# but we need logging available here to report configuration failures.
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Required environment variables — FAIL FAST if missing
# ---------------------------------------------------------------------------

GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    _log.critical(
        "GROQ_API_KEY environment variable is not set. "
        "Export it with: export GROQ_API_KEY='gsk_...'"
    )
    sys.exit(1)

GOOGLE_APPLICATION_CREDENTIALS: str = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS", ""
)
if not GOOGLE_APPLICATION_CREDENTIALS:
    _log.critical(
        "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set. "
        "Export it with: export GOOGLE_APPLICATION_CREDENTIALS='/path/to/key.json'"
    )
    sys.exit(1)

if not os.path.isfile(GOOGLE_APPLICATION_CREDENTIALS):
    _log.critical(
        f"GOOGLE_APPLICATION_CREDENTIALS points to a non-existent file: "
        f"{GOOGLE_APPLICATION_CREDENTIALS}"
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Groq / LLM constants
# ---------------------------------------------------------------------------

GROQ_MODEL: str = "llama-3.3-70b-versatile"

# Temperature for SQL generation — low value keeps output deterministic.
# Temperature for summarization and chart picking — slightly higher is fine.
SQL_TEMPERATURE: float = 0.1
SUMMARIZE_TEMPERATURE: float = 0.3
CHART_TEMPERATURE: float = 0.2

MAX_TOKENS: int = 1024          # Max tokens in LLM response
MAX_SQL_RETRIES: int = 2        # Max retries after dry-run failure (3 total attempts)

# ---------------------------------------------------------------------------
# BigQuery dataset / table constants
# ---------------------------------------------------------------------------

PROJECT_ID: str = "bigquery-public-data"
DATASET_ID: str = "new_york_taxi_trips"
TABLE_ID: str = "tlc_yellow_trips_2015"

# Fully-qualified table reference used in SQL generation prompts
FULL_TABLE_REF: str = f"`{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`"

# Maximum number of schema columns to include in the prompt before truncating.
# llama-3.3-70b-versatile has a 128k context window, but shorter prompts
# produce more reliable SQL.
MAX_SCHEMA_COLUMNS: int = 40

# Number of sample distinct values to fetch per column for the schema prompt.
SAMPLE_VALUES_PER_COLUMN: int = 3

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------

# Resolve project root as the parent of this config/ directory
PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE: str = os.path.join(PROJECT_ROOT, "output.log")
TEST_RESULTS_DIR: str = os.path.join(PROJECT_ROOT, "test_results")
