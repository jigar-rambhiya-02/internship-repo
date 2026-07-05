"""
src/utils/logger.py

Configures a project-wide logger that writes to BOTH:
  1. stdout (StreamHandler) — for live terminal feedback
  2. output.log in the project root (FileHandler, mode='a') — for persistence

Log format: TIMESTAMP | LEVEL | MESSAGE
Example:    2026-06-23 14:30:00,123 | INFO | Starting schema load

This module exposes a single function `get_logger(name)` that every other
module calls to obtain a correctly configured logger instance.

Design decision: Using a single shared FileHandler (attached to the root logger)
ensures all modules write to the same output.log without duplicating entries,
even if get_logger() is called multiple times with the same name.
"""

import logging
import sys
from config.settings import LOG_FILE

# ---------------------------------------------------------------------------
# Custom formatter — produces the required pipe-delimited format
# ---------------------------------------------------------------------------
_FORMATTER = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ---------------------------------------------------------------------------
# Flag to ensure handlers are attached to the root logger only once,
# even if get_logger() is called from multiple modules at import time.
# ---------------------------------------------------------------------------
_HANDLERS_CONFIGURED = False


def _configure_root_logger() -> None:
    """Attach FileHandler and StreamHandler to the root logger exactly once."""
    global _HANDLERS_CONFIGURED
    if _HANDLERS_CONFIGURED:
        return

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # Root captures everything; handlers filter

    # --- File handler: append to output.log in project root ---
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_FORMATTER)

    # --- Stream handler: write INFO+ to stdout ---
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(_FORMATTER)

    root.addHandler(file_handler)
    root.addHandler(stream_handler)

    _HANDLERS_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger. All named loggers propagate to the root logger,
    which holds the actual handlers (file + stream).

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        A configured logging.Logger instance.
    """
    _configure_root_logger()
    return logging.getLogger(name)
