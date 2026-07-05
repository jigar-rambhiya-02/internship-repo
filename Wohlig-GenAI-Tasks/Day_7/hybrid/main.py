"""
Hybrid RAG System Main Execution Entrypoint.

Error Handling Design Frameworks:
- FAIL-FAST: Validate key configurations, environment credentials, and data integrity parameters 
  at startup. Terminate immediately if anomalies are detected to prevent corrupted pipeline execution.
- GRACEFUL DEGRADATION: Intermittent validation loops are wrapped inside modular error catch-blocks, 
  ensuring individual runtime anomalies do not cause batch failures.
"""

import os
import sys
from dotenv import load_dotenv
from config.logger_config import setup_logger

# Initialize primary logging layout configuration
logger = setup_logger("main_entrypoint")

# Apply Fail-Fast Validation Step 1: Verify environment variables before importing dependent components
load_dotenv()
groq_key_check = os.getenv("GROQ_API_KEY")
if not groq_key_check or groq_key_check.strip() == "your_groq_api_key_here" or groq_key_check.strip() == "":
    logger.critical("FAIL-FAST CRASH: 'GROQ_API_KEY' configuration variable is completely absent or unassigned inside .env file.")
    print("CRITICAL SECURITY EXCEPTION: Environmental Setup Error. View output.log for details.", file=sys.stderr)
    sys.exit(1)

# Safely import dependent workflow classes after verification passing
from src.corpus_builder import generate_synthetic_corpus
from data.test_set_builder import generate_extended_test_set
from src.eval_harness import EvaluationHarness
from hybrid.retriever_hybrid import HybridRetriever
from src.groq_client import GroqGenerator

def main():
    logger.info("Executing pipeline initialization validation steps.")
    
    corpus_file_target = "data/corpus.json"
    test_set_file_target = "hybrid/test_set_extended.jsonl"
    results_csv_target = "hybrid/results.csv"
    
    # Core Infrastructure Provisioning Step
    try:
        logger.info("Constructing foundational corpus asset data structures.")
        generate_synthetic_corpus(output_path=corpus_file_target)
        
        logger.info("Compiling matrix question evaluation target paths.")
        generate_extended_test_set(output_path=test_set_file_target)
        
    except Exception as build_err:
        logger.critical(f"FAIL-FAST CRASH: System failed to establish foundational data files. Trace details: {str(build_err)}", exc_info=True)
        sys.exit(1)
        
    # Apply Fail-Fast Validation Step 2: Ensure critical execution paths exist on disk
    if not os.path.exists(corpus_file_target) or not os.path.exists(test_set_file_target):
        logger.critical("FAIL-FAST CRASH: Preflight file assertions failed. Output assets missing from designated data directories.")
        sys.exit(1)
        
    # Execute full Evaluation Harness suite
    logger.info("Invoking comprehensive cross-retriever benchmark analysis tests...")
    harness = EvaluationHarness(test_set_path=test_set_file_target, corpus_path=corpus_file_target)
    harness.execute_evaluation(output_csv=results_csv_target)
    
    # Sample Test Query Execution: Verifying Grounded Generation and RAG Connectivity
    logger.info("Executing validation check on final RAG compilation loop...")
    test_query = "What is the specific duty rate assigned to imported footwear matching HS code 6403?"
    
    try:
        hybrid_orchestrator = HybridRetriever(corpus_path=corpus_file_target)
        hybrid_orchestrator.initialize_indexes()
        
        # Retrieve the context chunks using the hybrid engine
        retrieved_context = hybrid_orchestrator.retrieve_top_5(test_query)
        
        # Initialize the Groq generation client
        generator = GroqGenerator()
        generation_response = generator.generate_grounded_answer(query=test_query, context_chunks=retrieved_context)
        
        logger.info("=== FINAL VERIFICATION RUN SUCCESSFUL ===")
        logger.info(f"Target Query: '{test_query}'")
        logger.info(f"Grounded System Output Response:\n{generation_response}")
        logger.info("Pipeline executed with zero unhandled exceptions. Verification complete.")
        
    except Exception as rag_err:
        logger.error(f"Grounded generation validation run failed: {str(rag_err)}", exc_info=True)
        print("ALERT: RAG generation phase encountered an error. Check output.log for diagnostic trace.", file=sys.stderr)

if __name__ == "__main__":
    main()

