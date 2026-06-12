import logging
import sys
from pathlib import Path

from config.settings import LOG_PATH


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger to write to both stdout and output.log."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
    ]

    root = logging.getLogger()
    root.setLevel(level)
    for h in handlers:
        h.setFormatter(formatter)
        root.addHandler(h)
