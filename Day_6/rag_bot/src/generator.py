"""
src/generator.py
----------------
Groq API caller with grounding prompt for the Grounded RAG Chatbot.

Provides two public functions:
  - build_context_block(chunks): Formats retrieved chunks into a labeled
    context block for injection into the LLM prompt.
  - generate_answer(question, chunks): Calls the Groq API with the
    grounding system prompt + context block + user question.

Hallucination prevention:
  - If chunks is empty, returns the "I couldn't find..." fallback
    immediately WITHOUT calling the Groq API.
  - The system prompt enforces citation requirements and no-answer rules.

Graceful degradation:
  - All Groq API errors are caught; a safe error message is returned.
"""

import os
import time

import groq
from dotenv import load_dotenv

from src.logger_config import get_logger

# --- Load environment variables ---
load_dotenv('/Users/jigar/Documents/jigar/Tasks/.env')

# --- Configuration ---
logger = get_logger("generator")

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MAX_TOKENS = 1024
GROQ_TEMPERATURE = 0.1  # Low temperature for factual, grounded responses

NO_ANSWER_RESPONSE = "I couldn't find this information in the provided documents."
ERROR_RESPONSE = "An error occurred while generating a response. Please try again."

# --- Grounding System Prompt ---
# This prompt is the core of hallucination prevention.
# It is embedded here AND documented in system_prompt.md.
SYSTEM_PROMPT = """You are a precise, grounded research assistant. You will be given a set of document chunks as your ONLY knowledge source for answering the user's question.

RULES — YOU MUST FOLLOW THESE WITHOUT EXCEPTION:
1. Answer ONLY using information explicitly present in the provided document chunks.
2. Every factual claim in your answer MUST include an inline citation in the format [doc_id:page].
3. If the provided chunks do not contain sufficient information to answer the question, you MUST respond with exactly: "I couldn't find this information in the provided documents." Do NOT attempt to answer from your training knowledge.
4. Do NOT infer, extrapolate, or guess. If it is not in the chunks, it does not exist for you.
5. Do NOT say things like "Based on my knowledge..." or "Generally speaking...". Only cite the chunks.
6. Be concise. Do not pad your answer with filler sentences."""


def build_context_block(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a numbered, labeled context block for the LLM prompt.

    Each chunk is prefixed with its [doc_id:page] citation reference so the LLM
    can use this label in its inline citations.

    Args:
        chunks: List of chunk dicts with keys 'text', 'doc_id', 'page'.

    Returns:
        A formatted multi-line string ready for injection into the prompt.

    Example output:
        CONTEXT DOCUMENTS:

        [1] Source: [annual_report:4]
        "Revenue for Q3 exceeded projections by 12%, driven by..."

        [2] Source: [technical_manual:11]
        "The safety valve must be tested every 6 months per..."
    """
    if not chunks:
        return "CONTEXT DOCUMENTS:\n\n(No relevant documents were retrieved.)"

    lines = ["CONTEXT DOCUMENTS:\n"]

    for i, chunk in enumerate(chunks, start=1):
        doc_id = chunk.get("doc_id", "unknown")
        page = chunk.get("page", "?")
        text = chunk.get("text", "").strip()
        citation_label = f"[{doc_id}:{page}]"

        lines.append(f"[{i}] Source: {citation_label}")
        lines.append(f'"{text}"')
        lines.append("")  # Blank line between chunks for readability

    return "\n".join(lines)


def generate_answer(question: str, chunks: list[dict]) -> str:
    """
    Generate a grounded, cited answer to the user's question using the Groq API.

    Pipeline:
      1. If chunks is empty → return NO_ANSWER_RESPONSE immediately (no API call).
      2. Build the context block from retrieved chunks.
      3. Construct the full user message: context block + question.
      4. Call Groq API with system prompt + user message.
      5. Return the model's response text.

    Args:
        question: The user's natural language question.
        chunks:   List of retrieved chunk dicts from the retriever.

    Returns:
        A string containing the model's answer with inline citations,
        the NO_ANSWER_RESPONSE if chunks are empty or insufficient,
        or the ERROR_RESPONSE if the API call fails.
    """
    # --- Step 1: Short-circuit if no chunks ---
    if not chunks:
        logger.info(
            "No chunks retrieved. Returning no-answer response without calling Groq API."
        )
        return NO_ANSWER_RESPONSE

    # --- Step 2: Build context block ---
    context_block = build_context_block(chunks)

    # --- Step 3: Construct the full user message ---
    user_message = (
        f"{context_block}\n\n"
        f"QUESTION: {question.strip()}\n\n"
        f"Remember: Answer ONLY from the context above. Include [doc_id:page] citations "
        f"for every factual claim. If the answer is not in the context, say exactly: "
        f'"{NO_ANSWER_RESPONSE}"'
    )

    prompt_length = len(SYSTEM_PROMPT) + len(user_message)
    logger.info(
        f"Calling Groq API. Chunks: {len(chunks)}, "
        f"Total prompt length: {prompt_length:,} characters."
    )
    logger.debug(f"User message preview (first 200 chars): {user_message[:200]}")

    # --- Step 4: Construct API payload ---
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    # --- Step 5: Call Groq API ---
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.error("GROQ_API_KEY environment variable is not set. Cannot call Groq API.")
        return ERROR_RESPONSE

    client = groq.Groq(api_key=groq_api_key)

    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=GROQ_MAX_TOKENS,
            temperature=GROQ_TEMPERATURE,
        )

        elapsed = time.time() - start_time
        answer = response.choices[0].message.content.strip()

        logger.info(
            f"Groq API response received in {elapsed:.3f}s. "
            f"Response length: {len(answer)} characters."
        )
        logger.debug(f"Response preview (first 100 chars): {answer[:100]}")

        return answer

    except groq.APIStatusError as e:
        elapsed = time.time() - start_time
        logger.error(
            f"Groq API status error after {elapsed:.3f}s: "
            f"Status {e.status_code} — {e.message}"
        )
        return ERROR_RESPONSE

    except groq.APIConnectionError as e:
        elapsed = time.time() - start_time
        logger.error(
            f"Groq API connection error after {elapsed:.3f}s: {e}"
        )
        return ERROR_RESPONSE

    except groq.RateLimitError as e:
        elapsed = time.time() - start_time
        logger.error(
            f"Groq API rate limit exceeded after {elapsed:.3f}s: {e}. "
            "Wait before retrying or reduce request frequency."
        )
        return ERROR_RESPONSE

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            f"Unexpected error during Groq API call after {elapsed:.3f}s: "
            f"{type(e).__name__}: {e}"
        )
        return ERROR_RESPONSE
