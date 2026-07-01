# !/usr/bin/env bash
# setup.sh — Scaffold the entire text2sql project in one command.
# Usage: chmod +x setup.sh && ./setup.sh

set -e  # Exit immediately on any error

echo "==> Creating directory structure..."

mkdir -p text2sql/config
mkdir -p text2sql/src/utils
mkdir -p text2sql/tests
mkdir -p text2sql/test_results

echo "==> Touching all source files..."

touch text2sql/config/__init__.py
touch text2sql/config/settings.py

touch text2sql/src/__init__.py
touch text2sql/src/utils/__init__.py
touch text2sql/src/utils/logger.py
touch text2sql/src/schema_loader.py
touch text2sql/src/sql_validator.py
touch text2sql/src/agent.py
touch text2sql/src/summarizer.py
touch text2sql/src/chart_picker.py

touch text2sql/tests/__init__.py
touch text2sql/tests/test_queries.py

touch text2sql/requirements.txt
touch text2sql/output.log
touch text2sql/dataset_choice.md
touch text2sql/test_queries.md
touch text2sql/learnings.md
touch text2sql/questions.md

echo "==> Creating blank README.md..."
echo "# Text-to-SQL BI Co-Pilot" > text2sql/README.md

echo "==> Creating Python virtual environment (myenv)..."
cd text2sql
python3 -m venv myenv

echo ""
echo "✅ Scaffold complete!"
echo ""
echo "Next steps:"
echo "  cd text2sql"
echo "  source myenv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  export GROQ_API_KEY=\"gsk_...\""
echo "  export GOOGLE_APPLICATION_CREDENTIALS=\"/path/to/key.json\""
echo "  python tests/test_queries.py"
