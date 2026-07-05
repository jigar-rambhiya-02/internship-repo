"""
utils/logger.py

Provides a dual-output (console + file) structured logger for the production RAG project.
Call setup_logger(name) once per module to get a configured logger instance.
"""

import logging
import os

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output.log")


def setup_logger(name: str) -> logging.Logger:
    """
    Create and return a logger with both console and file handlers.

    Handlers are only added if not already present, preventing duplicate log lines
    when a module is imported multiple times or the function is called more than once
    with the same name.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Guard: only add handlers if none exist yet
    if logger.handlers:
        return logger

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler — writes DEBUG and above to output.log
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
