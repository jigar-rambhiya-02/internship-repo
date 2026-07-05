from groq.resources import batches
from google.api_core.exceptions import NotFound
from google.api_core.exceptions import NonFound
from google.cloud import aiplatform
from google.cloud.aiplatform.matching_engine_index_endpoint import (
    MatchingEngineIndexEndpoint,
)

# pyrefly: ignore [missing-import]
from google.cloud.aiplatform_v1.types import IndexDatapoint

from utils.logger import get_logger

logger = get_logger()

_UPSERT_BATCH_SIZE = 100


def _vector_norm(vector: list) -> float:
    return sum(x*x for x in vector) ** 0.5

def upsert_chunks(chunks_with_embeddings: list, project: str, region: str, index_id: str) -> int:
    aiplatform.init(project = project, location = region)

    try:
        index = aiplatform.MatchingEngineIndex(index_name = index_id)
    except NonFound as e:
        logger.error(
            f'Vertex AI Index not found for index_id = "{index_id}".'
            f'Verify VERTEX_INDEX_ID is correct in .env. | {e}'
        )
        raise

    total_upserted = 0
    total_batches = (len(chunks_with_embeddings) + _UPSERT_BATCH_SIZE - 1) // _UPSERT_BATCH_SIZE

    for batch_number, batch_start in enumerate(
        range(0, len(chunks_with_embeddings), _UPSERT_BATCH_SIZE), start = 1
        ):
        batch_chunks = chunks_with_embeddings[batch_start: batch_start + _UPSERT_BATCH_SIZE]

        datapoints = []
        for chunk in batch:
            restricts = [
                IndexDatapoint.Restriction(namespace = 'year', allow_list = [str(chunk['year'])]),
                IndexDatapoint.Restriction(namespace = 'doc_type', allow_list = [str(chunk['doc_type'])]),
                IndexDatapoint.Restriction(namespace= 'doc_id', allow_list = [str(chunk['doc_id'])]),
            ]
            datapoints.append(
                IndexDatapoint(
                    datapoint_id = str(chunk['chunk_id']),
                    embedding = chunk['embedding'],
                    restricts = restricts
                )
            )
        
        try:
            index.upsert_datapoints(datapoints = datapoints)
            total_upserted += len(datapoints)
            logger.info(
                f'Upsert batch {batch_number}/{total_batches} complete | '
                f'datapoints_in_batch = {len(datapoints)} | total_upserted_so_far = {total_upserted}'
            )
        except NotFound as e:
            logger.error(f'Index not fount during upsert batch {batch_number}: {e}')
            raise

        except Exception as e:
            logger.error(f'Upsert batch {batch_number} failed: {type(e).__name__}: {e}. Skipping batch. ')
            continue
    return total_upserted

def query_index(
    query_embedding: list,
    top_k: int,
    project: str,
    region: str,
    index_endpoint_id: str,
    deployed_index_id: str,
    filter_namespaces: dict = None,
) -> list:
    
    aiplatform.init(project = project, location = region)

    norm = _vector_norm(query_embedding)
    logger.info(f'Querying Index | tok_k = {top_k} | query_vector_norm = {norm:.4f} | filters = {filter_namespaces}')

    try:
        endpoint = MatchingEngineIndexEndpoint(index_endpoint_name = index_endpoint_id)
    
    except NotFound as e:
        logger.error(
            f'Vertex AI IndexEndpoint not found for index_endpoint_id = "{index_endpoint_id}". '
            f'Verify VERTEX_INDEX_ENDPOINT_ID is correct in .env. | {e}'
        )
        raise

    restricts_param = None
    if filter_namespaces:
        restricts_param = [
            {'namespace': namespace, 'allow_list': [str(value)]}
            for namespace, value in filter_namespaces.items()
        ]

    try:
        response = endpoint.find_neighbors(
            deployed_index_id = deployed_index_id,
            queries = [query_embedding],
            num_neighbors = top_k,
            filter = restricts_param,
        )
    
    except NotFound as e:
        logger.error(
            f'Deployed index not found for deployed_index_id = "{deployed_index_id}" '
            f'on endpoint "{index_endpoint_id}". Verify VERTEX_DEPLOYED_INDEX_ID. | {e}'
        )
        raise

    results = []
    if response and len(response) > 0:
        for neighbor in response[0]:
            results.append({'chunk_id': neighbor.id, 'distance': neighbor.distance})

    logger.info(f'Query return {len(results)} results.')
    return results

