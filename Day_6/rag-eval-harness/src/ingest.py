# src/ingest.py
import hashlib
import time
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from config import settings
from src.utils import setup_logger, count_tokens

logger = setup_logger(__name__)


def load_corpus(data_dir: str) -> list[str]:
    texts = []
    data_path = Path(data_dir)
    if not data_path.exists():
        logger.error(f"Data directory not found: {data_dir}")
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    txt_files = sorted(data_path.glob("*.txt"))
    total_chars = 0

    for txt_file in txt_files:
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                text = f.read()
                texts.append(text)
                total_chars += len(text)
                logger.info(f"Loaded {txt_file.name}: {len(text)} chars")
        except Exception as e:
            logger.error(f"Failed to read {txt_file.name}: {e}")

    logger.info(f"Loaded {len(texts)} files, {total_chars} total characters")
    return texts


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    words = text.split()
    chunks = []
    if not words:
        return chunks

    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end == len(words):
            break
        start += chunk_size - overlap

    return chunks


def generate_chunk_id(text: str, index: int) -> str:
    content = f"{index}:{text[:50]}"
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def build_chroma_index(chunks: list[str], chunk_ids: list[str]) -> chromadb.Collection:
    client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    collection = client.get_or_create_collection(name="rag_corpus")

    embedder = SentenceTransformer(settings.EMBEDDING_MODEL)

    batch_size = 100
    total_batches = (len(chunks) + batch_size - 1) // batch_size
    for i in tqdm(range(0, len(chunks), batch_size), desc="Embedding & indexing"):
        batch_chunks = chunks[i : i + batch_size]
        batch_ids = chunk_ids[i : i + batch_size]
        embeddings = embedder.encode(batch_chunks, show_progress_bar=False).tolist()
        collection.upsert(ids=batch_ids, embeddings=embeddings, documents=batch_chunks)
        logger.info(f"Indexed batch {i // batch_size + 1}/{total_batches}")

    logger.info(f"Indexed {len(chunks)} chunks into ChromaDB collection 'rag_corpus'")
    return collection


def main():
    logger.info("=== Ingestion Pipeline Started ===")
    start = time.time()

    raw_texts = load_corpus("data/raw")
    all_chunks = []
    all_chunk_ids = []

    for doc_idx, text in enumerate(raw_texts):
        doc_chunks = chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        base_idx = len(all_chunks)
        for chunk_idx, chunk in enumerate(doc_chunks):
            global_idx = base_idx + chunk_idx
            chunk_id = generate_chunk_id(chunk, global_idx)
            all_chunks.append(chunk)
            all_chunk_ids.append(chunk_id)
        logger.info(f"Document {doc_idx}: chunked into {len(doc_chunks)} chunks")

    collection = build_chroma_index(all_chunks, all_chunk_ids)
    elapsed = time.time() - start
    logger.info(f"=== Ingestion Pipeline Completed in {elapsed:.2f}s ===")


if __name__ == "__main__":
    main()
