import time

from groq import Groq

from config.settings import GROQ_API_KEY
from utils.logger import get_logger

logger = get_logger()

# attach api-key = API_KEY

_MAX_RETRIES = 5
_BACKOFF_DELAYS_SECONDS = [2, 4, 8, 16, 32]
_INTER_BATCH_SLEEP_SECONDS = 1

def _embed_with_retry(text: str, model: str, task_type: str) -> list:
    last_exception = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            # response = genai.embed_content(model=model, content=text, task_type=task_type)
            return response["embedding"]
        except ResourceExhausted as e:
            last_exception = e
            if attempt < _MAX_RETRIES:
                delay = _BACKOFF_DELAYS_SECONDS[attempt]
                logger.info(
                    f"ResourceExhausted on embed_content (attempt {attempt + 1}/{_MAX_RETRIES}). "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"Exhausted all {_MAX_RETRIES} retries for embed_content due to ResourceExhausted.")
        except Exception as e:
            logger.error(f"Unhandled exception during embed_content: {type(e).__name__}: {e}")
            raise

    raise last_exception

def embed_chunks(chunks: list, model: str, batch_size: int = 20) -> list:

    embedded_chunks = []
    total_batches = (len(chunks) + batch_size - 1) // batch_size if chunks else 0

    for batch_number, batch_start in enumerate(range(0, len(chunks), batch_size), start = 1):
        batch = chunks[batch_start: batch_start + batch_size]
        retries_triggered_this_batch = 0

        for chunk in batch:
            try:
                embedding = _embed_with_retry(chunk['text'], model = model, task_type = 'RETRIEVAL_DOCUMENT')
                chunk_with_embedding = dict(chunk)
                chunk_with_embedding['embedding'] = embedding
                embedded_chunks.append(chunk_with_embedding)
            except ResourceExhausted:
                retries_triggered_this_batch += 1
                logger.error(f'Skipping chunk {chunk.get('chunk_id', '<unknown>')} after exhausting retries.')
                continue

        logger.info(
            f'Embedding batch {batch_number}/{total_batches} complete | '
            f'embedding_received = {len(batch) - retries_triggered_this_batch}/{len(batch)}'
            f'retries_triggered = {retries_triggered_this_batch}'
        )

        if batch_start + batch_size < len(chunks):
            time.sleep(_INTER_BATCH_SLEEP_SECONDS)

    return embedded_chunks

def embed_query(text: str, model: str) -> list:
    return _embed_with_retry(text, model = model, task_type = 'RETRIEVAL_QUERY')