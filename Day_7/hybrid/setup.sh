#!/bin/bash
set -e

echo "=== Initializing Advanced Hybrid RAG Workspace ==="

# 1. Create directory structure
mkdir -p config data hybrid src tests logs

# 2. Provision layout placeholders and files
touch config/logger_config.py
touch config/__init__.py
touch data/test_set_builder.py
touch data/__init__.py
touch hybrid/bm25_index.py
touch hybrid/__init__.py
touch hybrid/retriever_hybrid.py
touch hybrid/rrf.py
touch hybrid/when_hybrid_wins.md
touch src/corpus_builder.py
touch src/eval_harness.py
touch src/groq_client.py
touch src/retriever_dense.py
touch src/__init__.py
touch tests/test_rrf.py
touch tests/__init__.py
touch main.py

# 3. Write requirements.txt
cat << 'EOF' > requirements.txt
groq
python-dotenv
sentence-transformers
faiss-cpu
rank_bm25
numpy
pandas
pytest
EOF

# 4. Write .env.example
cat << 'EOF' > .env.example
GROQ_API_KEY=your_groq_api_key_here
EOF

# 5. Write baseline README placeholder
echo "# Advanced Hybrid RAG Project Workspace" > README.md

# 6. Initialize python environment
echo "=== Establishing Virtual Environment 'myenv' ==="
python3 -m venv myenv
source myenv/bin/activate

echo "=== Upgrading Package Managers ==="
pip install --upgrade pip

echo "=== Installing Dependencies from Pins ==="
pip install -r requirements.txt

echo "=== Workspace Setup Successfully Complete ==="
echo "To begin, verify the directory layout and add your GROQ_API_KEY to a local .env file."

