import json
import csv
import logging
from pathlib import Path
from typing import Generator

logger = logging.getLogger(__name__)


def load_corpus(corpus_dir: Path, extensions: tuple[str, ...] = (".txt", ".md")) -> dict[str, str]:
    """
    Load all documents from corpus_dir.

    Returns:
        dict mapping doc_id (filename stem) to document text.

    Raises:
        FileNotFoundError: If corpus_dir does not exist.
        ValueError: If corpus_dir contains no valid documents.
        UnicodeDecodeError: If any file is not UTF-8 encoded (fail-fast).
    """
    if not corpus_dir.exists():
        raise FileNotFoundError(
            f"Corpus directory not found: {corpus_dir}\n"
            f"Create it and add .txt or .md documents before running."
        )

    docs: dict[str, str] = {}
    for path in sorted(corpus_dir.iterdir()):
        if path.suffix.lower() not in extensions:
            continue
        text = path.read_text(encoding="utf-8")  # Raises UnicodeDecodeError on bad files
        if len(text.strip()) < 200:
            logger.warning("Skipping short document (< 200 chars): %s", path.name)
            continue
        docs[path.stem] = text

    if not docs:
        raise ValueError(
            f"No valid documents found in {corpus_dir}. "
            f"Expected files with extensions: {extensions}"
        )

    logger.info("Loaded %d documents from %s", len(docs), corpus_dir)
    return docs


def iter_jsonl(path: Path) -> Generator[dict, None, None]:
    """
    Yield parsed JSON objects from a JSONL file.

    Raises:
        FileNotFoundError: If path does not exist.
        json.JSONDecodeError: On malformed lines (fail-fast with line number).
    """
    if not path.exists():
        raise FileNotFoundError(f"JSONL file not found: {path}")

    with path.open(encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise json.JSONDecodeError(
                    f"Malformed JSON on line {line_num} of {path}: {exc.msg}",
                    exc.doc,
                    exc.pos,
                ) from exc


def write_results_csv(path: Path, rows: list[dict]) -> None:
    """Write evaluation results to CSV. Creates parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("Cannot write empty results to CSV.")

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Results written to %s (%d rows)", path, len(rows))
