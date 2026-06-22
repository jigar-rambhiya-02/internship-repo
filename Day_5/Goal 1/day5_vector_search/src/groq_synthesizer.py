import time 
from groq import Groq

from config.settings import GROQ_API_KEY
from utils.logger import get_logger

logger = get_logger()

_client = Grop(api_key = GROQ_API_KEY)

_MODEL = 'llama-3.3-70b-versatile'
_TEMPERATURE = 0.1
_MAX_TOKENS = 1024
_MAX_RETRIES = 3
_RETRY_DELAY_SECONDS = 5

_SYSTEM_PROMPT = (
    "You are a research assistant. Answer ONLY using the provided context chunks. "
    "If the answer is not in the content, say 'I cannot find this in the indexed documents.' "
    "Do not hallucinate. Cite chunk_ids inline."
)

def _format_context(retrieved_chunks: list) -> str:
    formatted_blocks = []

    for chunk in retrieved_chunks:
        header = (
            f"[Chunk ID: {chunk.get('chunk_id', 'unknown')} | "
            f"Doc: {chunk.get('title', 'unknown')} | "
            f"Year: {chunk.get('year', 'unkown')} | "
            f"Page: {chunk.get('page_number', 'unkown')}]"
        )
        formatted_blocks.append(f"{header}\n{chunk.get('text', '')}")
    return "\n\n".join(formatted_blocks)

def synthesize_answer(question: str, retrieved_chunks: list) -> str:
    context_block = _format_context(retrieved_chunks)
    user_message = (
        f"Context chunks:\n\n{context_block}\n\n"
        f"Question: {question}"
    )

    logger.info(f"Synthesizing answer | question = '{question}' | num_chunks = {len(retrieved_chunks)}")

    last_exception = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = _client.chat.completions.create(
                model = _MODEL,
                temperature = _TEMPERATURE,
                max_tokens = _MAX_TOKENS,
                message = [
                    {'role':'system', 'content':_SYSTEM_PROMPT},
                    {'role':  'user', 'content' : user_message },
                ],
            )
            answer = response.choices[0].message.content

            usage = getattr(response, 'usage', None)
            if usage is not None:
                logger.info(
                    f'Synthesis complete | prompt_tokens = {usage.prompt_tokens} | '
                    f'completion_tokens = {usage.completion_tokens} | total_tokens = {usage.total}'
                )
            else:
                logger.info('Synthesis complete | token usage unavailabke in response')
            
            return answer

        except (grop.APIError, grop.RateLimitError) as e:
            last_exception = e
            if attempt < _MAX_RETRIES - 1:
                logger.info(
                    f"Groq API error on attempt {attempt + 1}/{_MAX_RETRIES}: {type(e).__name__}. "
                    f"Retrying in {_RETRY_DELAY_SECONDS}"
                )
                time.sleep(_RETRY_DELAY_SECONDS)
            else:
                logger.error(f"Exhausted all {_MAX_RETRIES} retries for Groq synthesis: {e}")

    raise last_exception
