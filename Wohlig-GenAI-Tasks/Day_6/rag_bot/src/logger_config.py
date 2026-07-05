"""
src/logger_config.py
--------------------
Centralized logging configuration for the Grounded RAG Chatbot.

Provides a get_logger(name) factory that returns a logger which simultaneously:
  - Prints to stdout (StreamHandler)
  - Appends to logs/output.log (FileHandler)

Log format: TIMESTAMP | LEVEL | MODULE | MESSAGE
Example:    2025-01-15 14:32:01 | INFO | retriever | Loaded FAISS index with 1,204 vectors
"""

import logging
from pathlib import Path


# --- Constants ---
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "output.log"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Track which loggers have already been configured to avoid duplicate handlers
_configured_loggers: set[str] = set()


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger that writes to both console and logs/output.log.

    Args:
        name: The logger name — typically the module name (e.g., 'retriever',
              'generator', 'ingest'). Use __name__ from the calling module.

    Returns:
        A logging.Logger instance with StreamHandler and FileHandler attached.

    Example:
        from src.logger_config import get_logger
        logger = get_logger(__name__)
        logger.info("FAISS index loaded successfully.")
    """
    # Ensure the logs directory exists before trying to write to it
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)

    # Prevent duplicate handlers if get_logger is called multiple times
    # for the same name (common in module-level calls during reloads)
    if name in _configured_loggers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # --- Console Handler (stdout) ---
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    # --- File Handler (logs/output.log) ---
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    # Prevent log messages from propagating to the root logger
    # (avoids duplicate output if root logger is configured elsewhere)
    logger.propagate = False

    _configured_loggers.add(name)

    return logger
