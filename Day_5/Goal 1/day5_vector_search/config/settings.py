import os

from dotenv import load_dotenv

load_dotenv('/Users/jigar/Documents/jigar/Tasks/.env')

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GCP_PROJECT_ID = os.environ.get('GCP_PROJEC_ID')
GCP_REGION = os.environ.get('GCP_REGION')
VERTEX_INDEX_ID = os.environ.get('VERTEX_INDEX_ID')
VERTEX_INDEX_ENDPOINT_ID = os.environ.get('VERTEX_INDEX_ENDPOINT_ID')
VERTEX_DEPLOYED_INDEX_ID = os.environ.get('VERTEX_DEPLOYED_INDEX_ID')

EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'models/text-embedding-004')
EMBEDDING_DEMINSION = int(os.environ.get('EMBEDDING_DEMINSION', '768'))
CHUNK_SIZE_TOKENS = int(os.environ.get('CHUNK_SIZE_TOKENS', '512'))
CHUNK_OVERLAP_TOKENS = int(os.environ.get('CHUNK_OVERLAP_TOKENS', '64'))
TOP_K_RESULTS = int(os.environ.get('TOP_K_RESULTS','5'))

PDF_DATA_DIR = os.environ.get('PDF_DATA_DIR', 'data/pdfs')
MANIFEST_PATH = os.environ.get('MANIFEST_PATH', 'vss/corpus_manifest.csv')

_REQUIRED_KEYS = {
    'GROQ_API_KEY':GROQ_API_KEY,
    'GEMINI_API_KEY':GEMINI_API_KEY,
    'GCP_PROJECT_ID':GCP_PROJECT_ID,
    'VERTEX_INDEX_ID':VERTEX_INDEX_ID,
    'VERTEX_INDEX_ENDPOINT_ID':VERTEX_INDEX_ENDPOINT_ID,
    'VERTEX_DEPLOYED_INDEX_ID':VERTEX_DEPLOYED_INDEX_ID
}

def validate_setting() -> None:
    missing = [key for key, value in _REQUIRED_KEYS.items() if not value]
    
    if missing:
        raise EnvironmentError(
            'Missing required environment variable(s): ' + ', '.join(missing) + '. Check your .env file against .env.example.'
        )

