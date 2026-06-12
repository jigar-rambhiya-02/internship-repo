import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def _require(key: str) -> str:
    """Fail fast if a required environment variable is missing."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Check your .env file and ensure it contains: {key}=<value>"
        )
    return value


# ── API ──────────────────────────────────────────────────────────────────────
GROQ_API_KEY: str = _require("GROQ_API_KEY")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR = BASE_DIR / os.getenv("CORPUS_DIR", "data/corpus")
TEST_SET_PATH = BASE_DIR / "chunking" / "test_set.jsonl"
RESULTS_PATH = BASE_DIR / "chunking" / "results.csv"
WINNER_PATH = BASE_DIR / "chunking" / "winner.md"
LOG_PATH = BASE_DIR / "output.log"

# ── Chunking Parameters ───────────────────────────────────────────────────────
CHUNK_SIZE_TOKENS: int = int(os.getenv("CHUNK_SIZE_TOKENS", "256"))
OVERLAP_TOKENS: int = int(os.getenv("OVERLAP_TOKENS", "32"))
MAX_SEMANTIC_TOKENS: int = int(os.getenv("MAX_SEMANTIC_TOKENS", "512"))
OVERLAP_SENTENCES: int = 1

# ── Retrieval ─────────────────────────────────────────────────────────────────
TOP_K_SMALL: int = int(os.getenv("TOP_K_SMALL", "5"))
TOP_K_LARGE: int = int(os.getenv("TOP_K_LARGE", "10"))
