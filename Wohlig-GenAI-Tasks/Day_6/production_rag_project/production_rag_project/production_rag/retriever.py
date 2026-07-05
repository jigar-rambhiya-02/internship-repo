"""
production_rag/retriever.py

BaseRetriever wraps sentence-transformers embedding and ChromaDB vector search.
Instantiate once per pipeline run; reuse across multiple queries.
"""

from sentence_transformers import SentenceTransformer
from config.settings import EMBED_MODEL, CHROMA_PERSIST_DIR, TOP_K_RETRIEVAL
from utils.chroma_store import get_or_create_collection, query_collection
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseRetriever:
    """
    Embedding-based retriever backed by ChromaDB.

    Embeds queries with sentence-transformers and performs approximate
    nearest-neighbour search against a named ChromaDB collection.
    """

    def __init__(self, collection_name: str) -> None:
        """
        Initialise the retriever.

        Args:
            collection_name: Name of the ChromaDB collection to query
                             (e.g. 'naive_corpus' or 'contextual_corpus').
        """
        logger.info(f"Loading embedding model: {EMBED_MODEL}")
        self.model = SentenceTransformer(EMBED_MODEL)

        logger.info(f"Connecting to ChromaDB collection: '{collection_name}'")
        self.collection = get_or_create_collection(
            collection_name=collection_name,
            persist_dir=CHROMA_PERSIST_DIR,
        )
        self.collection_name = collection_name

    def embed(self, text: str) -> list[float]:
        """
        Embed a single text string.

        Args:
            text: Input text to embed.

        Returns:
            Embedding vector as a list of floats.
        """
        vector = self.model.encode(text, convert_to_numpy=True)
        return vector.tolist()

    def retrieve(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> list[dict]:
        """
        Retrieve the top_k most semantically similar chunks for a query.

        Args:
            query: User query string.
            top_k: Number of chunks to retrieve.

        Returns:
            List of chunk dicts with keys: chunk_id, text, score, metadata.
        """
        logger.info(
            f"Retrieving top-{top_k} chunks for query: '{query[:80]}...'"
            if len(query) > 80
            else f"Retrieving top-{top_k} chunks for query: '{query}'"
        )

        query_embedding = self.embed(query)
        chunks = query_collection(
            collection=self.collection,
            query_embedding=query_embedding,
            top_k=top_k,
        )

        if chunks:
            logger.info(
                f"Retrieved {len(chunks)} chunks. "
                f"Top result: score={chunks[0]['score']:.4f}, "
                f"preview='{chunks[0]['text'][:60]}...'"
            )
        else:
            logger.warning("No chunks retrieved — collection may be empty.")

        return chunks
