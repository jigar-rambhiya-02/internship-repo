"""
app.py
------
Gradio chat interface entry point for the Grounded RAG Chatbot.

Initializes the FAISS retriever on startup, then exposes a Gradio
ChatInterface that processes user messages through the full RAG pipeline:
  retrieve() → generate_answer() → return cited response.

Launch:
  python app.py

The Gradio interface will print a local URL and a public share URL.
"""

import gradio as gr

from src.logger_config import get_logger
from src.retriever import load_index, retrieve
from src.generator import generate_answer

# --- Initialization ---
logger = get_logger("app")

logger.info("=" * 60)
logger.info("Grounded RAG Chatbot — Starting up")
logger.info("=" * 60)

# Load the FAISS index at startup (not per-request)
# This is critical for performance: loading a FAISS index takes 0.1–2s
# depending on corpus size. We do it once here, not on every chat message.
logger.info("Initializing retriever: loading FAISS index...")
index, chunks = load_index()

if index is None:
    logger.error(
        "FAISS index could not be loaded. The chatbot will return "
        "empty responses. Please run 'python ingest.py' and restart."
    )
else:
    logger.info(f"Retriever ready. Index loaded with {index.ntotal:,} vectors.")

logger.info("Gradio interface initializing...")


# --- Core Chat Function ---
def chat(message: str, history: list[list[str]]) -> str:
    """
    Main chat handler. Called by Gradio on each user message submission.

    Args:
        message: The user's current input message (string).
        history: Gradio's conversation history — list of [user_msg, bot_msg] pairs.
                 Not used directly in this implementation (we don't pass history
                 to the LLM; each query is independent against the document corpus).

    Returns:
        A string containing the grounded, cited answer from the LLM,
        or an appropriate fallback message if retrieval or generation fails.
    """
    logger.info(f"New user message received (length={len(message)} chars).")
    logger.debug(f"User message: '{message}'")

    # --- Graceful degradation for empty input ---
    if not message or not message.strip():
        logger.warning("Empty message received from user.")
        return "Please enter a question."

    # --- Step 1: Retrieve relevant chunks ---
    try:
        retrieved_chunks = retrieve(message, top_k=5)
    except Exception as e:
        logger.error(f"Unexpected error during retrieval: {e}")
        retrieved_chunks = []

    logger.info(f"Chunks retrieved: {len(retrieved_chunks)}")

    # --- Step 2: Generate answer ---
    try:
        answer = generate_answer(message, retrieved_chunks)
    except Exception as e:
        logger.error(f"Unexpected error during answer generation: {e}")
        answer = "An error occurred while generating a response. Please try again."

    logger.info(
        f"Interaction complete. "
        f"Chunks used: {len(retrieved_chunks)}, "
        f"Answer length: {len(answer)} chars."
    )

    return answer


# --- Gradio Interface ---
demo = gr.ChatInterface(
    fn=chat,
    title="Grounded RAG Chatbot",
    description=(
        "Answers are grounded in uploaded documents only. "
        "All factual claims include inline citations in the format [doc_id:page]. "
        "If the documents do not contain the answer, the bot will say so — "
        "it will never hallucinate or guess."
    ),
    examples=[
        "What are the main findings described in the documents?",
        "Summarize the key recommendations from the report.",
        "What safety procedures are outlined in the manual?",
    ],
    theme=gr.themes.Soft(),
    retry_btn=None,
    undo_btn=None,
    clear_btn="Clear Chat",
)

logger.info("Gradio interface built. Launching...")

if __name__ == "__main__":
    demo.launch(
        share=True,
        debug=False,
        show_error=True,
    )
    logger.info("Gradio app launched. Check the terminal for the public share URL.")
