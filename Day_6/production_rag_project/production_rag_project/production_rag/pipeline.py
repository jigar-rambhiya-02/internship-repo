"""
production_rag/pipeline.py

RAGPipeline orchestrates the full retrieval → (optional re-rank) → generation cycle.
Instantiate with a config string to select which techniques are active.
"""

from config.settings import TOP_K_RETRIEVAL, TOP_K_FINAL
from production_rag.retriever import BaseRetriever
from production_rag.reranker import ReRanker
from production_rag.generator import Generator
from utils.logger import setup_logger

logger = setup_logger(__name__)

VALID_CONFIGS = {"naive", "reranked", "contextual", "both"}


class RAGPipeline:
    """
    Orchestrates document retrieval, optional re-ranking, and answer generation.

    Configurations:
        naive:       ChromaDB cosine similarity only; top-5 by score.
        reranked:    ChromaDB top-20 → re-ranker → top-5.
        contextual:  Contextual ChromaDB top-5 by score (no re-ranker).
        both:        Contextual ChromaDB top-20 → re-ranker → top-5.
    """

    def __init__(self, config: str) -> None:
        if config not in VALID_CONFIGS:
            raise ValueError(
                f"Invalid config '{config}'. Must be one of: {VALID_CONFIGS}."
            )

        self.config = config

        # Select correct ChromaDB collection based on config
        if config in {"contextual", "both"}:
            collection_name = "contextual_corpus"
        else:
            collection_name = "naive_corpus"

        # Instantiate components
        self.retriever = BaseRetriever(collection_name=collection_name)
        self.reranker = ReRanker() if config in {"reranked", "both"} else None
        self.generator = Generator()

        logger.info(
            f"RAGPipeline initialised. "
            f"Config='{config}', collection='{collection_name}', "
            f"reranker={'enabled' if self.reranker else 'disabled'}."
        )

    def run(self, query: str) -> dict:
        """
        Execute the full RAG pipeline for a single query.

        Args:
            query: User question string.

        Returns:
            Dict with keys:
                query            (str):        Original query.
                answer           (str):        LLM-generated answer.
                retrieved_chunks (list[dict]): Final top-k chunks passed to generator.
                config           (str):        Active pipeline configuration.
        """
        logger.info(f"[{self.config.upper()}] Running pipeline for: '{query[:80]}'")

        # Stage 1: Retrieve top-20 candidates
        candidates = self.retriever.retrieve(query, top_k=TOP_K_RETRIEVAL)

        # Stage 2: Re-rank or slice to top-5
        if self.reranker is not None:
            top_chunks = self.reranker.rerank(query, candidates, top_k=TOP_K_FINAL)
        else:
            top_chunks = sorted(candidates, key=lambda x: x.get("score", 0.0), reverse=True)
            top_chunks = top_chunks[:TOP_K_FINAL]

        # Stage 3: Generate answer
        answer = self.generator.generate(query, top_chunks)

        return {
            "query": query,
            "answer": answer,
            "retrieved_chunks": top_chunks,
            "config": self.config,
        }
