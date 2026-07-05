# src/utils.py
import json
import logging
import sys
from pathlib import Path

from config.settings import LOG_FILE_PATH


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(LOG_FILE_PATH, mode="a")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def count_tokens(text: str) -> int:
    # Heuristic: 1 word ≈ 1.3 tokens on average for English text.
    # This is a fast approximation. For production, use tiktoken or the model's tokenizer.
    return int(len(text.split()) * 1.3)


def load_jsonl(path: str) -> list[dict]:
    logger = setup_logger(__name__)
    data = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON on line {line_num} in {path}: {e}")
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        raise
    return data


def save_jsonl(data: list[dict], path: str) -> None:
    logger = setup_logger(__name__)
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        logger.info(f"Saved {len(data)} records to {path}")
    except Exception as e:
        logger.error(f"Error writing to {path}: {e}")
        raise
