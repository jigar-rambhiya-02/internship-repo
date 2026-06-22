#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="day5_vector_search"

echo "Creating project structure at ./${PROJECT_ROOT} ..."

mkdir -p "${PROJECT_ROOT}/vvs"
mkdir -p "${PROJECT_ROOT}/src"
mkdir -p "${PROJECT_ROOT}/config"
mkdir -p "${PROJECT_ROOT}/utils"
mkdir -p "${PROJECT_ROOT}/tests"
mkdir -p "${PROJECT_ROOT}/data/pdfs"
mkdir -p "${PROJECT_ROOT}/logs"

# vvs/
touch "${PROJECT_ROOT}/vvs/ingest.py"
touch "${PROJECT_ROOT}/vvs/query.py"
touch "${PROJECT_ROOT}/vvs/filtered_queries.md"
touch "${PROJECT_ROOT}/vvs/setup.md"

# src/
touch "${PROJECT_ROOT}/src/__init__.py"
touch "${PROJECT_ROOT}/src/pdf_parser.py"
touch "${PROJECT_ROOT}/src/chunker.py"
touch "${PROJECT_ROOT}/src/embedder.py"
touch "${PROJECT_ROOT}/src/vector_store.py"
touch "${PROJECT_ROOT}/src/groq_synthesizer.py"

# config/
touch "${PROJECT_ROOT}/config/__init__.py"
touch "${PROJECT_ROOT}/config/settings.py"

# utils/
touch "${PROJECT_ROOT}/utils/__init__.py"
touch "${PROJECT_ROOT}/utils/logger.py"

# tests/
touch "${PROJECT_ROOT}/tests/__init__.py"
touch "${PROJECT_ROOT}/tests/test_chunker.py"
touch "${PROJECT_ROOT}/tests/test_embedder.py"
touch "${PROJECT_ROOT}/tests/test_query.py"

# logs/
touch "${PROJECT_ROOT}/logs/.gitkeep"

# root files
touch "${PROJECT_ROOT}/output.log"
touch "${PROJECT_ROOT}/.env"

# corpus_manifest.csv with header row
cat > "${PROJECT_ROOT}/vvs/corpus_manifest.csv" << 'CSV_EOF'
doc_id,title,year,doc_type,num_pages,num_chunks
CSV_EOF

# .gitignore
cat > "${PROJECT_ROOT}/.gitignore" << 'GITIGNORE_EOF'
myenv/
.env
__pycache__/
*.pyc
output.log
data/pdfs/
logs/
GITIGNORE_EOF

# requirements.txt (pinned versions)
cat > "${PROJECT_ROOT}/requirements.txt" << 'REQ_EOF'
python-dotenv==1.0.1
pypdf==4.3.1
tiktoken==0.7.0
google-generativeai==0.7.2
google-cloud-aiplatform==1.62.0
groq==0.9.0
arxiv==2.1.3
pandas==2.2.2
REQ_EOF

# empty README
touch "${PROJECT_ROOT}/README.md"

echo "Project structure created successfully under ./${PROJECT_ROOT}"
echo "Next: cd ${PROJECT_ROOT} && bash setup.sh"
