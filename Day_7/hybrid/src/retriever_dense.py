import numpy as np
import faiss
import json
import os
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from config.logger_config import setup_logger

logger = setup_logger("retriever_dense")

class DenseRetriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Initializing dense embedding transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.corpus_chunks: List[Dict[str, Any]] = []

    def build_index(self, corpus_path: str):
        """
        Loads the json corpus, computes dense semantic embeddings locally via SentenceTransformers,
        and initializes an in-memory FAISS IndexFlatIP index configured for cosine similarity tracking.
        """
        logger.info(f"Loading corpus for dense indexing from: {corpus_path}")
        if not os.path.exists(corpus_path):
            logger.error(f"Corpus file missing at {corpus_path}")
            raise FileNotFoundError(f"Corpus file missing: {corpus_path}")
            
        with open(corpus_path, "r", encoding="utf-8") as f:
            self.corpus_chunks = json.load(f)
            
        texts = [chunk["text"] for chunk in self.corpus_chunks]
        logger.info(f"Extracting {len(texts)} chunks. Computing embedding matrices...")
        
        # Compute embeddings and normalize them to unit length to ensure Inner Product calculates Cosine Similarity
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        embeddings = embeddings.astype('float32')
        faiss.normalize_L2(embeddings)
        
        dimension = embeddings.shape[1]
        logger.info(f"Embedding matrix shape: {embeddings.shape}. Initializing FAISS IndexFlatIP.")
        
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)
        logger.info("Dense vector index successfully established.")

    def search(self, query: str, top_k: int = 20) -> List[Tuple[str, int]]:
        """
        Encodes query, normalizes, executes flat inner product search against FAISS,
        and returns a 1-indexed rank list of tuples: (chunk_id, rank)
        """
        if self.index is None:
            logger.error("Search attempted before vector index was built.")
            raise ValueError("FAISS Index is not built yet.")
            
        query_vector = self.model.encode([query], convert_to_numpy=True).astype('float32')
        faiss.normalize_L2(query_vector)
        
        scores, indices = self.index.search(query_vector, top_k)
        
        ranked_results = []
        for rank_idx, corpus_idx in enumerate(indices[0]):
            if corpus_idx == -1:
                continue
            chunk_id = self.corpus_chunks[corpus_idx]["chunk_id"]
            # 1-indexed position assignment
            ranked_results.append((chunk_id, rank_idx + 1))
            
        return ranked_results

