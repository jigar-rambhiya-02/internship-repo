# setup.sh
#!/bin/bash
set -e

PROJECT_NAME="rag-eval-harness"
echo "Setting up $PROJECT_NAME..."

# Create directory structure
mkdir -p data/raw
mkdir -p src
mkdir -p eval
mkdir -p tests
mkdir -p config

# Create empty Python package and source files
touch src/__init__.py
touch src/ingest.py
touch src/rag_bot.py
touch src/utils.py
touch eval/judges.py
touch eval/run_eval.py
touch eval/test_set.jsonl
touch eval/results.csv
touch eval/eval_report.md
touch tests/test_judges.py
touch tests/test_rag_bot.py
touch config/settings.py
touch requirements.txt
touch guide.md
touch output.log

# Create virtual environment (name: myenv, NOT venv)
python3 -m venv myenv

# Create .gitignore
cat > .gitignore << 'EOF'
myenv/
.env
output.log
__pycache__/
*.pyc
chroma_db/
EOF

# Create .env.example
cat > .env.example << 'EOF'
GROQ_API_KEY=your_key_here
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
groq>=0.9.0
chromadb>=0.5.0
sentence-transformers>=3.0.0
pandas>=2.0.0
matplotlib>=3.8.0
jsonlines>=4.0.0
python-dotenv>=1.0.0
tqdm>=4.66.0
pytest>=8.0.0
EOF

# Install dependencies inside the virtual environment
source myenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete. Activate the environment with: source myenv/bin/activate"
