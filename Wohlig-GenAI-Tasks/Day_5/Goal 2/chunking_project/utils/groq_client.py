"""
Thin wrapper around the Groq API.
Used for metadata generation and evaluation explanation — NOT for embeddings.
"""

import logging
from typing import Optional
from groq import Groq

from config.settings import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)
_client: Optional[Groq] = None


def get_client() -> Groq:
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise EnvironmentError("GROQ_API_KEY is not set. Check your .env file.")
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def chat_complete(system_prompt: str, user_message: str, max_tokens: int = 512) -> str:
    """
    Single-turn chat completion via Groq.

    Raises:
        groq.APIError: On any API-level failure (fail-fast).
    """
    client = get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError(
            f"Groq returned an empty response for model '{GROQ_MODEL}'. "
            "Check your API quota and the request payload."
        )
    return content.strip()