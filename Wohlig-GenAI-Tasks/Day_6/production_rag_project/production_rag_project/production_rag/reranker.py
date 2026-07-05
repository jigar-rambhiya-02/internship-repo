"""
production_rag/reranker.py

ReRanker wraps the Vertex AI Ranking API with a BM25 + cosine hybrid fallback.
Vertex AI is used when GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT are set.
Otherwise the local fallback activates automatically — no configuration required.
"""

import os
import math
from rank_bm25 import BM25Okapi
from config.settings import TOP_K_FINAL, VERTEX_PROJECT_ID, VERTEX_LOCATION
from utils.logger import setup_logger

logger = setup_logger(__name__)

_CREDENTIALS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
_USE_VERTEX = bool(_CREDENTIALS_PATH and VERTEX_PROJECT_ID)


class ReRanker:
    """
    Two-mode re-ranker: Vertex AI neural re-ranking (primary) or BM25 + cosine
    hybrid scoring (fallback). Mode is selected automatically at instantiation.
    """

    def __init__(self) -> None:
        self.use_vertex = _USE_VERTEX
        if self.use_vertex:
            logger.info(
                "ReRanker mode: Vertex AI Ranking API "
                f"(project='{VERTEX_PROJECT_ID}', location='{VERTEX_LOCATION}')."
            )
        else:
            logger.info(
                "ReRanker mode: LOCAL fallback (BM25 + cosine hybrid). "
                "Set GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT to enable Vertex AI."
            )

    def rerank(
        self,
        query: str,
        chunks: list[dict],
        top_k: int = TOP_K_FINAL,
    ) -> list[dict]:
        """
        Re-rank chunks by relevance to the query and return the top_k results.

        Attempts Vertex AI if configured, falls back to local hybrid on any error.

        Args:
            query:  User query string.
            chunks: Candidate chunks from the retriever (each dict has 'text', 'score', etc.).
            top_k:  Number of results to return after re-ranking.

        Returns:
            List of up to top_k chunk dicts, augmented with 'rerank_score'.
        """
        if not chunks:
            logger.warning("ReRanker received empty chunk list; returning empty list.")
            return []

        if self.use_vertex:
            try:
                return self._rerank_vertex(query, chunks, top_k)
            except Exception as exc:
                logger.error(
                    f"Vertex AI re-ranking failed ({type(exc).__name__}: {exc}). "
                    "Falling back to local BM25 + cosine hybrid."
                )
                return self._rerank_local(query, chunks, top_k)
        else:
            return self._rerank_local(query, chunks, top_k)

    # ── Vertex AI re-ranking ───────────────────────────────────────────────────

    def _rerank_vertex(
        self,
        query: str,
        chunks: list[dict],
        top_k: int,
    ) -> list[dict]:
        """
        Call the Vertex AI Discovery Engine Ranking API to re-rank chunks.

        Raises:
            Any exception from the google-cloud-discoveryengine SDK, which the
            caller (rerank) will catch and route to the fallback.
        """
        from google.cloud import discoveryengine_v1 as discoveryengine
        from google.api_core.exceptions import GoogleAPICallError  # noqa: F401

        client = discoveryengine.RankServiceClient()

        ranking_config = client.ranking_config_path(
            project=VERTEX_PROJECT_ID,
            location=VERTEX_LOCATION,
            ranking_config="default_ranking_config",
        )

        records = [
            discoveryengine.RankingRecord(
                id=chunk["chunk_id"],
                title="",
                content=chunk["text"][:512],  # API has content length limits
            )
            for chunk in chunks
        ]

        request = discoveryengine.RankRequest(
            ranking_config=ranking_config,
            model="semantic-ranker-512@latest",
            top_n=top_k,
            query=query,
            records=records,
        )

        response = client.rank(request=request)

        # Build a lookup from chunk_id → original chunk dict
        chunk_map = {c["chunk_id"]: c for c in chunks}

        reranked = []
        for record in response.records:
            chunk = dict(chunk_map[record.id])  # shallow copy
            chunk["rerank_score"] = record.score
            reranked.append(chunk)

        logger.info(
            f"Vertex AI re-ranking: {len(chunks)} in → {len(reranked)} out. "
            f"Top score: {reranked[0]['rerank_score']:.4f}."
        )
        return reranked

    # ── Local BM25 + cosine hybrid re-ranking ─────────────────────────────────

    def _rerank_local(
        self,
        query: str,
        chunks: list[dict],
        top_k: int,
    ) -> list[dict]:
        """
        Hybrid BM25 + cosine re-ranker.

        Score formula:
            hybrid_score = 0.4 * bm25_norm + 0.6 * cosine_score

        BM25 scores are normalized to [0, 1] by dividing by the max BM25 score
        in the candidate set. Cosine scores from ChromaDB are already in [0, 1].

        The 0.4/0.6 weighting gives slightly more weight to semantic similarity
        (cosine) while BM25 provides a lexical recall signal for exact-match terms.
        """
        query_tokens = query.lower().split()
        tokenized_corpus = [c["text"].lower().split() for c in chunks]

        bm25 = BM25Okapi(tokenized_corpus)
        bm25_scores = bm25.get_scores(query_tokens)

        # Normalize BM25 to [0, 1]
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
        bm25_norm = [s / max_bm25 for s in bm25_scores]

        scored = []
        for i, chunk in enumerate(chunks):
            cosine = chunk.get("score", 0.0)
            hybrid = 0.4 * bm25_norm[i] + 0.6 * cosine
            enriched = dict(chunk)
            enriched["rerank_score"] = round(hybrid, 6)
            scored.append(enriched)

        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        result = scored[:top_k]

        logger.info(
            f"Local BM25+cosine re-ranking: {len(chunks)} in → {len(result)} out. "
            f"Top score: {result[0]['rerank_score']:.4f}."
        )
        return result
