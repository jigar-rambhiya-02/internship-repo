"""
ingest.py
---------
One-time document ingestion pipeline for the Grounded RAG Chatbot.

This script:
  1. Scans data/ for .pdf and .txt files
  2. Loads each file with appropriate LangChain loaders
  3. Chunks documents using RecursiveCharacterTextSplitter
  4. Embeds all chunks using sentence-transformers (all-MiniLM-L6-v2)
  5. Builds a FAISS IndexFlatL2 and saves it to faiss_index/

Run once before launching app.py:
  python ingest.py

Graceful degradation:
  - Empty data/ directory: logs WARNING and exits cleanly.
  - Unsupported file types: logs WARNING and skips the file.
  - Embedding failures: logs ERROR, skips that chunk, continues.
"""

import os
import sys
import time
import pickle
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.logger_config import get_logger

# --- Configuration ---
logger = get_logger("ingest")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = BASE_DIR / "faiss_index"
INDEX_FILE = INDEX_DIR / "index.faiss"
CHUNKS_FILE = INDEX_DIR / "chunks.pkl"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


def load_documents(data_dir: Path) -> list[dict]:
    """
    Scan data_dir for supported files and load them using LangChain loaders.

    Returns:
        A list of dicts with keys: 'text' (str), 'doc_id' (str), 'page' (int).
        Returns an empty list if no supported files are found.
    """
    logger.info(f"Scanning '{data_dir}' for documents...")

    # Check if data directory exists
    if not data_dir.exists():
        logger.warning(f"Data directory '{data_dir}' does not exist. Creating it now.")
        data_dir.mkdir(parents=True, exist_ok=True)

    # Find all files
    all_files = list(data_dir.iterdir())
    supported_files = [f for f in all_files if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    unsupported_files = [f for f in all_files if f.is_file() and f.suffix.lower() not in SUPPORTED_EXTENSIONS and not f.name.startswith(".")]

    if unsupported_files:
        for f in unsupported_files:
            logger.warning(f"Unsupported file type, skipping: '{f.name}' (extension '{f.suffix}')")

    if not supported_files:
        logger.warning(
            f"No supported files (.pdf, .txt) found in '{data_dir}'. "
            "Please add documents before running ingest.py."
        )
        return []

    logger.info(f"Found {len(supported_files)} supported file(s): {[f.name for f in supported_files]}")

    raw_documents = []

    for file_path in supported_files:
        doc_id = file_path.stem  # filename without extension, used as citation ID
        logger.info(f"Loading '{file_path.name}' (doc_id='{doc_id}')...")

        try:
            if file_path.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(file_path))
                pages = loader.load()
                for page_doc in pages:
                    raw_documents.append({
                        "text": page_doc.page_content,
                        "doc_id": doc_id,
                        "page": page_doc.metadata.get("page", 0) + 1  # 0-indexed → 1-indexed
                    })
                logger.info(f"  → Loaded {len(pages)} page(s) from '{file_path.name}'")

            elif file_path.suffix.lower() == ".txt":
                loader = TextLoader(str(file_path), encoding="utf-8")
                docs = loader.load()
                for i, doc in enumerate(docs):
                    raw_documents.append({
                        "text": doc.page_content,
                        "doc_id": doc_id,
                        "page": i + 1
                    })
                logger.info(f"  → Loaded {len(docs)} section(s) from '{file_path.name}'")

        except Exception as e:
            logger.error(f"Failed to load '{file_path.name}': {e}. Skipping this file.")
            continue

    logger.info(f"Total raw document sections loaded: {len(raw_documents)}")
    return raw_documents


def chunk_documents(raw_documents: list[dict]) -> list[dict]:
    """
    Split raw document sections into overlapping chunks.

    Each input dict has 'text', 'doc_id', 'page'.
    Each output dict has 'text' (the chunk text), 'doc_id', 'page'.

    Returns:
        A list of chunk dicts ready for embedding.
    """
    logger.info(f"Chunking {len(raw_documents)} document sections "
                f"(chunk_size={CHUNK_SIZE}, chunk_overlap={CHUNK_OVERLAP})...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    all_chunks = []

    for doc in raw_documents:
        if not doc["text"].strip():
            logger.debug(f"Skipping empty section from doc_id='{doc['doc_id']}', page={doc['page']}")
            continue

        try:
            sub_chunks = splitter.split_text(doc["text"])
            for chunk_text in sub_chunks:
                if chunk_text.strip():  # Skip any whitespace-only chunks
                    all_chunks.append({
                        "text": chunk_text.strip(),
                        "doc_id": doc["doc_id"],
                        "page": doc["page"]
                    })
        except Exception as e:
            logger.error(f"Failed to chunk doc_id='{doc['doc_id']}', page={doc['page']}: {e}. Skipping.")
            continue

    logger.info(f"Total chunks created: {len(all_chunks)}")
    return all_chunks


def embed_chunks(chunks: list[dict], model: SentenceTransformer) -> np.ndarray:
    """
    Embed all chunk texts using the provided SentenceTransformer model.

    Args:
        chunks: List of chunk dicts with 'text' key.
        model: Loaded SentenceTransformer model.

    Returns:
        A numpy array of shape (len(chunks), embedding_dim) as float32.
        Chunks that fail to embed are assigned a zero vector and logged as errors.
    """
    logger.info(f"Embedding {len(chunks)} chunks using '{EMBEDDING_MODEL_NAME}'...")
    start_time = time.time()

    texts = [chunk["text"] for chunk in chunks]

    try:
        # batch_size=32 is a safe default for CPU inference
        embeddings = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=False  # FAISS IndexFlatL2 does not require normalized vectors
        )
        embeddings = embeddings.astype(np.float32)
    except Exception as e:
        logger.error(f"Batch embedding failed: {e}. Attempting chunk-by-chunk fallback...")
        embedding_dim = model.get_sentence_embedding_dimension()
        embeddings = np.zeros((len(chunks), embedding_dim), dtype=np.float32)

        for i, text in enumerate(texts):
            try:
                vec = model.encode([text], convert_to_numpy=True).astype(np.float32)
                embeddings[i] = vec[0]
            except Exception as inner_e:
                logger.error(
                    f"Failed to embed chunk {i} (doc_id='{chunks[i]['doc_id']}', "
                    f"page={chunks[i]['page']}): {inner_e}. Using zero vector."
                )
                # Zero vector stays in place — this chunk will not be retrieved correctly
                # but it won't crash the pipeline

    elapsed = time.time() - start_time
    logger.info(f"Embedding complete. Time elapsed: {elapsed:.2f}s. "
                f"Embedding shape: {embeddings.shape}")
    return embeddings


def build_and_save_faiss_index(embeddings: np.ndarray, chunks: list[dict]) -> None:
    """
    Build a FAISS IndexFlatL2 from embeddings and save index + chunk metadata to disk.

    Args:
        embeddings: numpy array of shape (N, D) as float32.
        chunks: List of chunk dicts (parallel array to embeddings).
    """
    logger.info("Building FAISS IndexFlatL2...")

    embedding_dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(embeddings)

    logger.info(f"FAISS index built. Total vectors: {index.ntotal}, Dimension: {embedding_dim}")

    # Ensure output directory exists
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    # Save binary FAISS index
    faiss.write_index(index, str(INDEX_FILE))
    logger.info(f"FAISS index saved to '{INDEX_FILE}'")

    # Save chunk metadata (text + doc_id + page) as a pickle file
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(chunks, f)
    logger.info(f"Chunk metadata saved to '{CHUNKS_FILE}' ({len(chunks)} entries)")


def main() -> None:
    """
    Main ingestion pipeline. Orchestrates: load → chunk → embed → save.
    Exits cleanly with a log message if data/ is empty.
    """
    logger.info("=" * 60)
    logger.info("Starting document ingestion pipeline")
    logger.info("=" * 60)

    # Step 1: Load documents
    raw_documents = load_documents(DATA_DIR)

    if not raw_documents:
        logger.warning(
            "No documents were loaded. Ingestion pipeline aborted. "
            "Please add .pdf or .txt files to the data/ directory and re-run."
        )
        sys.exit(0)

    # Step 2: Chunk documents
    chunks = chunk_documents(raw_documents)

    if not chunks:
        logger.warning("No chunks were produced from the loaded documents. Aborting.")
        sys.exit(0)

    # Step 3: Load embedding model
    logger.info(f"Loading embedding model '{EMBEDDING_MODEL_NAME}'...")
    try:
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info(f"Model loaded. Embedding dimension: {model.get_sentence_embedding_dimension()}")
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        sys.exit(1)

    # Step 4: Embed chunks
    embeddings = embed_chunks(chunks, model)

    # Step 5: Build and save FAISS index
    build_and_save_faiss_index(embeddings, chunks)

    logger.info("=" * 60)
    logger.info("Ingestion pipeline complete. You may now run: python app.py")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
