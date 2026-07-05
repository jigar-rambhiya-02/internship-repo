"""
src/retriever.py
----------------
FAISS index loader and semantic retriever for the Grounded RAG Chatbot.

Provides two public functions:
  - load_index(): Loads the FAISS index and chunk metadata from disk.
  - retrieve(query, top_k): Embeds a query and returns the top-k most
    semantically similar chunks with their metadata and L2 scores.

Graceful degradation:
  - If the FAISS index is not found, load_index() logs an ERROR and
    returns (None, None) without raising an exception.
  - retrieve() checks for a None index and returns an empty list safely.
"""

import time
import pickle
from pathlib import Path
from typing import Tuple
from typing import Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from src.logger_config import get_logger

# --- Configuration ---
logger = get_logger("retriever")

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_DIR = BASE_DIR / "faiss_index"
INDEX_FILE = INDEX_DIR / "index.faiss"
CHUNKS_FILE = INDEX_DIR / "chunks.pkl"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Module-level state: loaded once at startup, reused for all queries
_index: Optional[faiss.Index] = None
_chunks: Optional[list[dict]] = None
_model: Optional[SentenceTransformer] = None



def load_index() -> Tuple[Optional[faiss.Index], Optional[list[dict]]]:
    global _index, _chunks, _model
    """
    Load the FAISS index and chunk metadata from disk.

    Sets module-level _index, _chunks, and _model for reuse.

    Returns:
        Tuple of (faiss.Index, list[dict]) on success.
        Tuple of (None, None) on failure — caller must handle gracefully.
    """
    logger.info("Loading FAISS index and chunk metadata...")

    # --- Check for index files ---
    if not INDEX_FILE.exists():
        logger.error(
            f"FAISS index file not found at '{INDEX_FILE}'. "
            "Please run 'python ingest.py' first."
        )
        return None, None

    if not CHUNKS_FILE.exists():
        logger.error(
            f"Chunk metadata file not found at '{CHUNKS_FILE}'. "
            "Please run 'python ingest.py' first."
        )
        return None, None

    # --- Load FAISS index ---
    try:
        _index = faiss.read_index(str(INDEX_FILE))
        logger.info(
            f"FAISS index loaded. Total vectors: {_index.ntotal:,}, "
            f"Dimension: {_index.d}"
        )
    except Exception as e:
        logger.error(f"Failed to load FAISS index: {e}")
        return None, None

    # --- Load chunk metadata ---
    try:
        with open(CHUNKS_FILE, "rb") as f:
            _chunks = pickle.load(f)
        logger.info(f"Chunk metadata loaded. Total chunks: {len(_chunks):,}")
    except Exception as e:
        logger.error(f"Failed to load chunk metadata: {e}")
        return None, None

    # --- Load embedding model ---
    try:
        logger.info(f"Loading embedding model '{EMBEDDING_MODEL_NAME}'...")
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("Embedding model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        return None, None

    return _index, _chunks


def retrieve(query: str, top_k: int = 5) -> Optional[list[dict]]:
    global _index, _chunks, _model
    if _index is None or _chunks is None or _model is None:
        logger.error(
            "Retriever is not initialized. Call load_index() before retrieve(). "
            "Returning empty chunk list."
        )
        return []

    if not query or not query.strip():
        logger.warning("Empty query received. Returning empty chunk list.")
        return []

    logger.debug(f"Retrieving top-{top_k} chunks for query: '{query[:80]}...'")
    start_time = time.time()

    try:
        query_vector = _model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=False
        ).astype(np.float32)
    except Exception as e:
        logger.error(f"Failed to embed query: {e}. Returning empty chunk list.")
        return []

    try:
        effective_k = min(top_k, _index.ntotal)
        if effective_k < top_k:
            logger.warning(
                f"Requested top_k={top_k} but index only has {_index.ntotal} vectors. "
                f"Retrieving {effective_k} chunks instead."
            )
        distances, indices = _index.search(query_vector, effective_k)
    except Exception as e:
        logger.error(f"FAISS search failed: {e}. Returning empty chunk list.")
        return []

    elapsed = time.time() - start_time
    """
    Embed a query and retrieve the top-k most similar chunks from the FAISS index.

    Args:
        query: The user's natural language question.
        top_k: Number of chunks to retrieve (default: 5).

    Returns:
        A list of dicts, each containing:
          - "text"   (str):   The chunk text content.
          - "doc_id" (str):   Source document identifier (filename without extension).
          - "page"   (int):   Page or section number within the source document.
          - "score"  (float): L2 distance from query vector (lower = more similar).

        Returns an empty list if the index is not loaded or if retrieval fails.
    """
    # --- Embed the query ---
    try:
        query_vector = _model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=False
        ).astype(np.float32)
        # query_vector shape: (1, embedding_dim)
    except Exception as e:
        logger.error(f"Failed to embed query: {e}. Returning empty chunk list.")
        return []

    # --- FAISS similarity search ---
    try:
        # Clamp top_k to the number of available vectors
        effective_k = min(top_k, _index.ntotal)
        if effective_k < top_k:
            logger.warning(
                f"Requested top_k={top_k} but index only has {_index.ntotal} vectors. "
                f"Retrieving {effective_k} chunks instead."
            )

        # faiss.search returns:
        #   distances: shape (1, effective_k) — L2 distances (float32)
        #   indices:   shape (1, effective_k) — chunk indices (int64)
        distances, indices = _index.search(query_vector, effective_k)
    except Exception as e:
        logger.error(f"FAISS search failed: {e}. Returning empty chunk list.")
        return []

    elapsed = time.time() - start_time

    # --- Build results list ---
    results = []
    retrieved_summary = []

    for rank, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        if idx == -1:
            # FAISS returns -1 for indices when the index has fewer vectors than k
            logger.debug(f"Rank {rank+1}: No result (index returned -1). Skipping.")
            continue

        chunk = _chunks[idx]
        result = {
            "text": chunk["text"],
            "doc_id": chunk["doc_id"],
            "page": chunk["page"],
            "score": float(dist)
        }
        results.append(result)
        retrieved_summary.append(f"[{chunk['doc_id']}:{chunk['page']}] (score={dist:.4f})")

    logger.info(
        f"Retrieval complete in {elapsed:.3f}s. "
        f"Retrieved {len(results)} chunk(s): {', '.join(retrieved_summary)}"
    )

    return results
