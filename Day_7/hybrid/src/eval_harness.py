import json
import os
import pandas as pd
from typing import List, Dict, Any
from src.retriever_dense import DenseRetriever
from hybrid.bm25_index import BM25Retriever
from hybrid.retriever_hybrid import HybridRetriever
from config.logger_config import setup_logger

logger = setup_logger("eval_harness")

class EvaluationHarness:
    def __init__(self, test_set_path: str = "hybrid/test_set_extended.jsonl", corpus_path: str = "data/corpus.json"):
        self.test_set_path = test_set_path
        self.corpus_path = corpus_path
        
        # Instantiate retrieval variants
        self.dense_retriever = DenseRetriever()
        self.bm25_retriever = BM25Retriever()
        self.hybrid_retriever = HybridRetriever(corpus_path=corpus_path)

    def execute_evaluation(self, output_csv: str = "hybrid/results.csv"):
        """
        Iterates over the 40 test queries, calculates individual recall numbers,
        implements graceful error handling, and writes the results out to results.csv.
        """
        logger.info("Priming validation engines for broad run.")
        self.dense_retriever.build_index(self.corpus_path)
        self.bm25_retriever.build_index(self.corpus_path)
        self.hybrid_retriever.initialize_indexes()
        
        if not os.path.exists(self.test_set_path):
            logger.critical(f"Test dataset absent at system target: {self.test_set_path}")
            raise FileNotFoundError(f"Missing evaluation file: {self.test_set_path}")
            
        questions: List[Dict[str, Any]] = []
        with open(self.test_set_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    questions.append(json.loads(line.strip()))
                    
        logger.info(f"Loaded {len(questions)} evaluation tracking queries. Starting execution loop.")
        
        evaluation_records = []
        skipped_count = 0
        
        for q in questions:
            q_id = q["question_id"]
            query_str = q["query"]
            q_type = q["query_type"]
            gold_id = q["gold_chunk_id"]
            
            # Implementation of the Graceful Degradation Strategy via localized try-except blocks
            try:
                # 1. Evaluate Dense Only (Top-5 extraction)
                dense_res = self.dense_retriever.search(query_str, top_k=5)
                dense_top_5_ids = [chunk_id for chunk_id, _ in dense_res]
                dense_recall = 1 if gold_id in dense_top_5_ids else 0
                
                # 2. Evaluate BM25 Only (Top-5 extraction)
                bm25_res = self.bm25_retriever.search(query_str, top_k=5)
                bm25_top_5_ids = [chunk_id for chunk_id, _ in bm25_res]
                bm25_recall = 1 if gold_id in bm25_top_5_ids else 0
                
                # 3. Evaluate Hybrid RRF Engine (Top-5 extraction natively mapped)
                hybrid_res = self.hybrid_retriever.retrieve_top_5(query_str)
                hybrid_top_5_ids = [chunk["chunk_id"] for chunk in hybrid_res]
                hybrid_recall = 1 if gold_id in hybrid_top_5_ids else 0
                
                logger.info(f"Eval metrics for {q_id} ({q_type}) -> Dense Recall: {dense_recall} | BM25 Recall: {bm25_recall} | Hybrid Recall: {hybrid_recall}")
                
                evaluation_records.append({
                    "question_id": q_id,
                    "query_type": q_type,
                    "dense_recall": dense_recall,
                    "bm25_recall": bm25_recall,
                    "hybrid_recall": hybrid_recall
                })
                
            except Exception as loop_error:
                logger.error(f"Graceful degradation caught error at question tracking index {q_id}: {str(loop_error)}", exc_info=True)
                skipped_count += 1
                continue
                
        # Consolidate matrix allocations into persistent dataframe formats
        df_results = pd.DataFrame(evaluation_records)
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df_results.to_csv(output_csv, index=False)
        
        logger.info("=== EVALUATION HARNESS SUMMARY ===")
        logger.info(f"Processed evaluations successfully written directly to: {output_csv}")
        logger.info(f"Total rows exported: {len(evaluation_records)} | Total runtime errors bypassed: {skipped_count}")
        
        # Calculate and log summary metrics
        if not df_results.empty:
            summary = df_results.groupby("query_type")[["dense_recall", "bm25_recall", "hybrid_recall"]].mean()
            logger.info(f"\nMean recall profiles computed across subsets:\n{summary.to_string()}")
