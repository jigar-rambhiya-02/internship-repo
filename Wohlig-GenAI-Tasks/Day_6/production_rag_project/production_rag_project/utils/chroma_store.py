"""
utils/chroma_store.py

ChromaDB client factory and collection management utilities.
Provides get_or_create_collection, upsert_chunks, and query_collection.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from utils.logger import setup_logger

logger = setup_logger(__name__)


def get_or_create_collection(
    collection_name: str,
    persist_dir: str,
) -> chromadb.Collection:
    """
    Initialize a persistent ChromaDB client and return the named collection,
    creating it if it does not already exist.

    Args:
        collection_name: Name of the ChromaDB collection.
        persist_dir:     Directory path for ChromaDB on-disk persistence.

    Returns:
        chromadb.Collection instance.
    """
    client = chromadb.PersistentClient(
        path=persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    logger.info(
        f"ChromaDB collection '{collection_name}' ready "
        f"(persist_dir='{persist_dir}', count={collection.count()})."
    )
    return collection


def upsert_chunks(
    collection: chromadb.Collection,
    chunks: list[dict],
    embeddings: list[list[float]],
) -> None:
    """
    Upsert a batch of chunks and their pre-computed embeddings into a ChromaDB collection.

    Args:
        collection: Target ChromaDB collection.
        chunks:     List of chunk dicts (must include 'chunk_id', 'text', 'page', 'source').
        embeddings: Parallel list of embedding vectors (one per chunk).
    """
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"Chunk count ({len(chunks)}) and embedding count ({len(embeddings)}) must match."
        )

    ids = [c["chunk_id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [{"page": c["page"], "source": c["source"]} for c in chunks]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    logger.info(f"Upserted {len(chunks)} chunks into collection '{collection.name}'.")


def query_collection(
    collection: chromadb.Collection,
    query_embedding: list[float],
    top_k: int,
) -> list[dict]:
    """
    Query a ChromaDB collection by embedding vector and return the top_k results.

    Args:
        collection:      ChromaDB collection to query.
        query_embedding: Embedding of the query string.
        top_k:           Number of nearest neighbours to return.

    Returns:
        List of dicts, each containing:
            chunk_id (str):   Document ID.
            text     (str):   Document text.
            score    (float): Cosine similarity score (higher = more similar).
            metadata (dict):  Page and source metadata.
    """
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "distances", "metadatas"],
    )

    chunks = []
    ids = results["ids"][0]
    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    for chunk_id, text, distance, meta in zip(ids, documents, distances, metadatas):
        # ChromaDB cosine distance: score = 1 - distance  (higher score = more similar)
        score = 1.0 - distance
        chunks.append(
            {
                "chunk_id": chunk_id,
                "text": text,
                "score": round(score, 6),
                "metadata": meta,
            }
        )

    return chunks
