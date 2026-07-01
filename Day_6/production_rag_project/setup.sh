# Create all directories
mkdir -p production_rag_project/{data,production_rag,config,utils,tests}

cd production_rag_project

# Create Python package files
touch production_rag/__init__.py
touch production_rag/reranker.py
touch production_rag/contextualizer.py
touch production_rag/retriever.py
touch production_rag/generator.py
touch production_rag/evaluator.py
touch production_rag/pipeline.py

touch config/__init__.py
touch config/settings.py

touch utils/__init__.py
touch utils/logger.py
touch utils/pdf_loader.py
touch utils/chroma_store.py

touch tests/__init__.py
touch tests/test_reranker.py
touch tests/test_contextualizer.py
touch tests/test_evaluator.py

# Create root-level files
touch lift_report.md questions.md .env .gitignore requirements.txt README.md

# Create virtual environment
python -m venv myenv

# Activate (macOS/Linux)
source myenv/bin/activate

# Activate (Windows — run this instead of the line above)
# myenv\Scripts\activate

echo "Scaffold complete. Activate your environment and install requirements."
