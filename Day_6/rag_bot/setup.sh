#!/usr/bin/env bash
# =============================================================================
# setup.sh — Full project scaffold for Grounded RAG Chatbot
# Run this from the PARENT directory of where you want rag_bot/ to live.
# Usage: bash setup.sh
# =============================================================================

set -e  # Exit immediately on any error

echo "=============================================="
echo "  Grounded RAG Chatbot — Project Scaffold"
echo "=============================================="

# --- Step 1: Create directory structure ---
echo "[1/6] Creating project directory structure..."

mkdir -p rag_bot/data
mkdir -p rag_bot/faiss_index
mkdir -p rag_bot/screenshots
mkdir -p rag_bot/logs
mkdir -p rag_bot/src

# Create placeholder files so git tracks empty directories
touch rag_bot/data/.gitkeep
touch rag_bot/faiss_index/.gitkeep
touch rag_bot/screenshots/.gitkeep
touch rag_bot/logs/.gitkeep

# Create all source files as empty placeholders
touch rag_bot/src/__init__.py
touch rag_bot/src/logger_config.py
touch rag_bot/src/retriever.py
touch rag_bot/src/generator.py
touch rag_bot/app.py
touch rag_bot/ingest.py
touch rag_bot/system_prompt.md
touch rag_bot/no_answer_demo.md
touch rag_bot/guide.md

echo "    ✓ Directory structure created."

# --- Step 2: Create requirements.txt ---
echo "[2/6] Writing requirements.txt..."

cat > rag_bot/requirements.txt << 'EOF'
groq==0.9.0
faiss-cpu==1.8.0
sentence-transformers==3.0.1
langchain==0.2.14
langchain-community==0.2.12
pypdf==4.3.1
gradio==4.42.0
python-dotenv==1.0.1
numpy==1.26.4
EOF

echo "    ✓ requirements.txt written."

# --- Step 3: Create .env template ---
echo "[3/6] Writing .env template..."

cat > rag_bot/.env << 'EOF'
GROQ_API_KEY=your_groq_api_key_here
EOF

echo "    ✓ .env template created. IMPORTANT: Add your real Groq API key before running."

# --- Step 4: Create .gitignore ---
echo "[4/6] Writing .gitignore..."

cat > rag_bot/.gitignore << 'EOF'
# Environment
.env
myenv/
__pycache__/
*.pyc
*.pyo
.DS_Store

# Generated artifacts
faiss_index/
logs/

# Python packaging
*.egg-info/
dist/
build/
EOF

echo "    ✓ .gitignore created."

# --- Step 5: Create virtual environment ---
echo "[5/6] Creating Python virtual environment 'myenv'..."

cd rag_bot
python3 -m venv myenv
echo "    ✓ Virtual environment 'myenv' created."

# --- Step 6: Activate and install dependencies ---
echo "[6/6] Installing dependencies into myenv..."

# Activate the virtual environment
source myenv/bin/activate

pip install --upgrade pip --quiet
pip install -r requirements.txt

echo ""
echo "=============================================="
echo "  ✓ Scaffold complete!"
echo "=============================================="
echo ""
echo "  NEXT STEPS:"
echo "  1. cd rag_bot"
echo "  2. source myenv/bin/activate          (Linux/Mac)"
echo "     OR: myenv\\Scripts\\activate.bat    (Windows)"
echo "  3. Edit .env and add your real GROQ_API_KEY"
echo "  4. Add PDF or TXT files to the data/ directory"
echo "  5. python ingest.py"
echo "  6. python app.py"
echo "=============================================="
