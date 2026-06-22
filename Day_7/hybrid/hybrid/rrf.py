from typing import List, Tuple, Dict
from config.logger_config import setup_logger

logger = setup_logger("rrf_engine")

def compute_rrf(dense_results: List[Tuple[str, int]], bm25_results: List[Tuple[str, int]], k: int = 60) -> List[Tuple[str, float]]:
    """
    Executes Reciprocal Rank Fusion on two independent ranking lists.
    Formula: score(chunk) = Sum_{lists} [ 1 / (k + rank) ]
    Input structure expects a sequence of (chunk_id, 1_indexed_rank) pairs.
    Returns a sorted array of tuples containing (chunk_id, combined_rrf_score).
    """
    rrf_scores: Dict[str, float] = {}
    
    # Process Dense results list
    for chunk_id, rank in dense_results:
        if chunk_id not in rrf_scores:
            rrf_scores[chunk_id] = 0.0
        rrf_scores[chunk_id] += 1.0 / (k + rank)
        
    # Process BM25 results list
    for chunk_id, rank in bm25_results:
        if chunk_id not in rrf_scores:
            rrf_scores[chunk_id] = 0.0
        rrf_scores[chunk_id] += 1.0 / (k + rank)
        
    # Sort documents in descending order of their total combined score
    sorted_rrf = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
    
    return sorted_rrf

