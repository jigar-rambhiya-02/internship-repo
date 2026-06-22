import json
from typing import List, Dict, Any
from src.retriever_dense import DenseRetriever
from hybrid.bm25_index import BM25Retriever
from hybrid.rrf import compute_rrf
from config.logger_config import setup_logger

logger = setup_logger("hybrid_retriever")

class HybridRetriever:
    def __init__(self, corpus_path: str = "data/corpus.json"):
        self.corpus_path = corpus_path
        self.dense_engine = DenseRetriever()
        self.bm25_engine = BM25Retriever()
        self.chunks_lookup: Dict[str, Dict[str, Any]] = {}
        
    def initialize_indexes(self):
        """
        Coordinates dual indexing across both dense vector spaces and sparse token indexes.
        """
        logger.info("Initializing baseline indexes for hybrid pipeline.")
        self.dense_engine.build_index(self.corpus_path)
        self.bm25_engine.build_index(self.corpus_path)
        
        # Load raw reference registry to quickly resolve text payloads from chunk IDs
        with open(self.corpus_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            self.chunks_lookup = {c["chunk_id"]: c for c in raw_data}
        logger.info("Hybrid search engines actively primed.")

    def retrieve_top_5(self, query: str) -> List[Dict[str, Any]]:
        """
        Executes concurrent retrieval, runs dense top-20 and BM25 top-20 queries,
        applies RRF fusion math, and isolates the final top 5 documents.
        """
        dense_candidates = self.dense_engine.search(query, top_k=20)
        bm25_candidates = self.bm25_engine.search(query, top_k=20)
        
        # Perform reciprocal ranking fusion calculation
        fused_rankings = compute_rrf(dense_candidates, bm25_candidates, k=60)
        top_5_fused = fused_rankings[:5]
        
        final_context_chunks = []
        for chunk_id, rrf_score in top_5_fused:
            chunk_data = self.chunks_lookup[chunk_id].copy()
            chunk_data["rrf_score"] = rrf_score
            final_context_chunks.append(chunk_data)
            
        return final_context_chunks

