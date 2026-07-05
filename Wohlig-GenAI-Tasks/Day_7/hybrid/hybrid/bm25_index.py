import json
import os
import re
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi
from config.logger_config import setup_logger

logger = setup_logger("bm25_index")

class BM25Retriever:
    def __init__(self):
        self.corpus_chunks: List[Dict[str, Any]] = []
        self.bm25 = None

    def _tokenize(self, text: str) -> List[str]:
        """
        Splits strings on non-alphanumeric boundaries while keeping identifiers 
        such as 'ABC-2024-117' or '8.2.1' unbroken by lowercasing words and grouping spaces.
        """
        # Convert to lowercase and split by spaces/punctuation, retaining internal dashes and decimals
        tokens = re.findall(r'[a-zA-Z0-9.\-]+', text.lower())
        return tokens

    def build_index(self, corpus_path: str):
        """
        Ingests corpus text data, tokenizes text, and loads inverted document frequency structures.
        """
        logger.info(f"Loading corpus for BM25 processing from: {corpus_path}")
        if not os.path.exists(corpus_path):
            logger.error(f"Corpus file not located at {corpus_path}")
            raise FileNotFoundError(f"Corpus missing: {corpus_path}")
            
        with open(corpus_path, "r", encoding="utf-8") as f:
            self.corpus_chunks = json.load(f)
            
        logger.info(f"Tokenizing {len(self.corpus_chunks)} text documents for Okapi BM25 index entry.")
        tokenized_corpus = [self._tokenize(chunk["text"]) for chunk in self.corpus_chunks]
        
        self.bm25 = BM25Okapi(tokenized_corpus)
        logger.info("BM25 structural term-frequency inverted index successfully initialized.")

    def search(self, query: str, top_k: int = 20) -> List[Tuple[str, int]]:
        """
        Calculates BM25 query weights across document indexes and outputs sorted top_k tuples (chunk_id, rank).
        """
        if self.bm25 is None:
            logger.error("BM25 search invoked without active model state index.")
            raise ValueError("BM25 matrix index uninitialized.")
            
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get sorted structural offsets
        sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        ranked_results = []
        for rank_idx, corpus_idx in enumerate(sorted_indices):
            # Exclude scores of 0 to ensure non-matching terms do not inflate ranks
            if scores[corpus_idx] <= 0.0:
                continue
            chunk_id = self.corpus_chunks[corpus_idx]["chunk_id"]
            ranked_results.append((chunk_id, rank_idx + 1))
            
        return ranked_results

