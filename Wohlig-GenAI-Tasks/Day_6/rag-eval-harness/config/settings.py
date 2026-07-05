# config/settings.py
from typing import Final

GROQ_MODEL: Final[str] = "llama-3.3-70b-versatile"
EMBEDDING_MODEL: Final[str] = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE: Final[int] = 512
CHUNK_OVERLAP: Final[int] = 128
TOP_K_RETRIEVAL: Final[int] = 5
CHROMA_PERSIST_DIR: Final[str] = "chroma_db"
EVAL_TEST_SET_PATH: Final[str] = "eval/test_set.jsonl"
EVAL_RESULTS_PATH: Final[str] = "eval/results.csv"
LOG_FILE_PATH: Final[str] = "output.log"
SCORE_THRESHOLD: Final[float] = 0.6
