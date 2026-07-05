"""
production_rag/contextualizer.py

Generates LLM context prefixes for each chunk (Groq API) and indexes the enriched
chunks into a separate ChromaDB collection named 'contextual_corpus'.

Run once as a pre-processing step before executing the eval harness.
"""

import os
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv('/Users/jigar/Documents/jigar/Tasks/.env')

from config.settings import (
    GROQ_MODEL,
    EMBED_MODEL,
    CHROMA_PERSIST_DIR,
    CORPUS_PDF_PATH,
)
from utils.logger import setup_logger
from utils.pdf_loader import load_and_chunk_pdf
from utils.chroma_store import get_or_create_collection, upsert_chunks

logger = setup_logger(__name__)

CONTEXT_SYSTEM_PROMPT = (
    "You are a document indexing assistant. Respond with exactly one sentence "
    "(max 25 words) that describes what this chunk is about and where it appears "
    "in the document. No preamble."
)

BATCH_SIZE = 20  # Upsert to ChromaDB in batches of this size


def generate_context_prefix(
    chunk_text: str,
    doc_title: str,
    groq_client: Groq,
) -> str:
    """
    Generate a one-sentence context prefix for a chunk using the Groq API.

    On any API error, logs the exception and returns an empty string so the chunk
    is still indexed (without a prefix) rather than dropped.

    Args:
        chunk_text:  Text of the chunk to describe.
        doc_title:   Title or filename of the source document.
        groq_client: Initialized Groq client.

    Returns:
        A single-sentence context string, or "" on failure.
    """
    user_prompt = f"Document: {doc_title}\nChunk text: {chunk_text[:800]}"

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": CONTEXT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            max_tokens=60,
        )
        prefix = response.choices[0].message.content.strip()
        return prefix
    except Exception as exc:
        logger.error(
            f"Groq context prefix generation failed ({type(exc).__name__}: {exc}). "
            "Using empty prefix for this chunk."
        )
        return ""


def contextualize_corpus(
    pdf_path: str = CORPUS_PDF_PATH,
    collection_name: str = "contextual_corpus",
) -> None:
    """
    Load a PDF, generate LLM context prefixes for each chunk, and index the
    enriched chunks into a dedicated ChromaDB collection.

    Args:
        pdf_path:        Path to the source PDF.
        collection_name: Target ChromaDB collection name (default: 'contextual_corpus').
    """
    logger.info(f"Starting contextual corpus indexing from: {pdf_path}")

    # Load PDF and chunk
    chunks = load_and_chunk_pdf(pdf_path)
    total_chunks = len(chunks)
    doc_title = os.path.basename(pdf_path)

    # Initialise clients
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    embed_model = SentenceTransformer(EMBED_MODEL)

    # Initialise ChromaDB collection
    collection = get_or_create_collection(
        collection_name=collection_name,
        persist_dir=CHROMA_PERSIST_DIR,
    )

    groq_calls = 0
    estimated_tokens = 0
    batch_chunks: list[dict] = []
    batch_embeddings: list[list[float]] = []

    for idx, chunk in enumerate(chunks, start=1):
        # Generate context prefix
        prefix = generate_context_prefix(
            chunk_text=chunk["text"],
            doc_title=doc_title,
            groq_client=groq_client,
        )
        groq_calls += 1
        # Rough token estimate: (prefix words + chunk words) * 1.3 subword factor
        estimated_tokens += int((len(prefix.split()) + len(chunk["text"].split())) * 1.3)

        # Prepend prefix to chunk text
        enriched_text = f"{prefix}\n{chunk['text']}" if prefix else chunk["text"]
        enriched_chunk = dict(chunk)
        enriched_chunk["text"] = enriched_text

        # Embed enriched text
        embedding = embed_model.encode(enriched_text, convert_to_numpy=True).tolist()

        batch_chunks.append(enriched_chunk)
        batch_embeddings.append(embedding)

        # Progress logging every 10 chunks
        if idx % 10 == 0 or idx == total_chunks:
            logger.info(f"Processed {idx}/{total_chunks} chunks.")

        # Batch upsert
        if len(batch_chunks) >= BATCH_SIZE or idx == total_chunks:
            upsert_chunks(collection, batch_chunks, batch_embeddings)
            batch_chunks = []
            batch_embeddings = []

    logger.info(
        f"Contextual corpus indexing complete. "
        f"Total chunks: {total_chunks}, "
        f"Groq API calls: {groq_calls}, "
        f"Estimated tokens used: {estimated_tokens:,}."
    )


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    contextualize_corpus()
