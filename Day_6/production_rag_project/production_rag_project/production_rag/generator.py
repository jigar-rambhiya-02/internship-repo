"""
production_rag/generator.py

Generator wraps the Groq API to produce answers grounded in retrieved context.
Uses temperature=0 for deterministic, reproducible outputs during evaluation.
"""

import os
import groq 

from dotenv import load_dotenv
load_dotenv('/Users/jigar/Documents/jigar/Tasks/.env')


from config.settings import GROQ_MODEL
from utils.logger import setup_logger

logger = setup_logger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the user's question using ONLY the provided context. "
    "If the context does not contain the answer, say 'I cannot answer this from the provided context.' "
    "Be concise and factual."
)


class Generator:
    """
    Groq-backed answer generator. Grounds answers strictly in the provided
    context chunks to maximise RAGAS faithfulness scores.
    """

    def __init__(self) -> None:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY environment variable is not set.")
        self.client = groq.Groq(api_key=api_key)
        logger.info(f"Generator initialised with model: {GROQ_MODEL}")

    def generate(self, query: str, context_chunks: list[dict]) -> str:
        """
        Generate an answer for the given query using the top context chunks.

        Args:
            query:          User question.
            context_chunks: Retrieved and (optionally) re-ranked chunks.

        Returns:
            Answer string, or a graceful degradation message on API failure.
        """
        if not context_chunks:
            logger.warning("Generator received no context chunks; returning fallback message.")
            return "I cannot answer this from the provided context."

        # Build context block
        context_string = "\n\n---\n\n".join(c["text"] for c in context_chunks)

        user_prompt = f"Context:\n{context_string}\n\nQuestion: {query}"

        logger.debug(
            f"Generating answer for: '{query[:80]}' "
            f"using {len(context_chunks)} context chunks."
        )

        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
                max_tokens=512,
            )

            answer = response.choices[0].message.content.strip()
            token_count = response.usage.completion_tokens if response.usage else "unknown"

            logger.info(
                f"Answer generated. "
                f"Tokens: {token_count}. "
                f"Preview: '{answer[:80]}...'" if len(answer) > 80 else f"Answer: '{answer}'"
            )
            return answer

        except groq.RateLimitError as exc:
            logger.error(f"Groq rate limit reached: {exc}. Returning fallback message.")
            return "Generation failed due to API error."
        except groq.APIError as exc:
            logger.error(f"Groq API error: {exc}. Returning fallback message.")
            return "Generation failed due to API error."
        except Exception as exc:
            logger.error(f"Unexpected generator error ({type(exc).__name__}: {exc}).")
            return "Generation failed due to API error."
