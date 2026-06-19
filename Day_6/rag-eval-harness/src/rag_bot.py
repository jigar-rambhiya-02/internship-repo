# src/rag_bot.py
import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer

from config import settings
from src.utils import setup_logger

logger = setup_logger(__name__)

_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedder


def retrieve(
    query: str, collection: chromadb.Collection, top_k: int
) -> tuple[list[str], list[str]]:
    embedder = _get_embedder()
    query_embedding = embedder.encode([query], show_progress_bar=False).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents"],
    )

    documents = results["documents"][0] if results["documents"] else []
    ids = results["ids"][0] if results["ids"] else []

    logger.info(f"Retrieved {len(documents)} chunks for query")
    return documents, ids


def generate_answer(question: str, context_chunks: list[str], client: Groq) -> str:
    context_text = "\n\n---\n\n".join(context_chunks)

    system_prompt = (
        "You are a grounded assistant. Answer ONLY using the provided context. "
        "If the context does not contain the answer, say: 'I cannot answer this from the provided context.' "
        "Do not use any outside knowledge."
    )

    user_prompt = f"Context:\n{context_text}\n\nQuestion: {question}\n\nAnswer:"

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            max_tokens=1024,
        )
        answer = response.choices[0].message.content.strip()
        logger.info(f"Generated answer ({len(answer)} chars)")
        return answer
    except Exception as e:
        logger.error(f"Groq API error during generation: {e}", exc_info=True)
        return "ERROR: Generation failed."


def get_rag_response(
    question: str, collection: chromadb.Collection, client: Groq
) -> dict:
    try:
        retrieved_chunks, retrieved_chunk_ids = retrieve(
            question, collection, settings.TOP_K_RETRIEVAL
        )
        answer = generate_answer(question, retrieved_chunks, client)
        return {
            "question": question,
            "answer": answer,
            "retrieved_chunks": retrieved_chunks,
            "retrieved_chunk_ids": retrieved_chunk_ids,
        }
    except Exception as e:
        logger.error(
            f"RAG pipeline failed for question '{question[:50]}...': {e}",
            exc_info=True,
        )
        return {
            "question": question,
            "answer": "ERROR: RAG pipeline failed.",
            "retrieved_chunks": [],
            "retrieved_chunk_ids": [],
        }
