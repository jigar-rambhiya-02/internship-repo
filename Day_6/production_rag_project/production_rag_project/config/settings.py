"""
config/settings.py

Centralized project configuration. All modules import constants from here.
Environment-sensitive values (API keys, GCP project) are read at module load time
from environment variables; set them in .env and call load_dotenv() before importing.
"""

import os

# ── Model identifiers ──────────────────────────────────────────────────────────
GROQ_MODEL: str = "llama-3.3-70b-versatile"
EMBED_MODEL: str = "all-MiniLM-L6-v2"

# ── Retrieval configuration ────────────────────────────────────────────────────
TOP_K_RETRIEVAL: int = 20   # Candidates fetched from ChromaDB before re-ranking
TOP_K_FINAL: int = 5        # Chunks passed to the generator after re-ranking

# ── Storage paths ──────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR: str = "./chroma_store"
CORPUS_PDF_PATH: str = "./data/corpus.pdf"
LOG_FILE: str = "output.log"
RESULTS_CSV: str = "./production_rag/results.csv"

# ── GCP / Vertex AI ───────────────────────────────────────────────────────────
VERTEX_PROJECT_ID: str = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
VERTEX_LOCATION: str = os.environ.get("VERTEX_LOCATION", "global")

# ── Evaluation questions and ground truths ─────────────────────────────────────
# These are domain-appropriate for a generic annual report / business document corpus.
# Ground truths are synthetic but plausible; label them clearly in any client-facing output.

EVAL_QUESTIONS: list[str] = [
    "What was the company's total revenue for the fiscal year?",
    "Which business segment reported the highest operating margin?",
    "What were the primary risk factors identified by management?",
    "How did the company's headcount change compared to the prior year?",
    "What capital expenditure projects were announced or completed?",
    "What dividend or share buyback actions were taken during the year?",
    "Who are the members of the executive leadership team?",
    "What geographic markets showed the strongest revenue growth?",
]

EVAL_GROUND_TRUTHS: list[str] = [
    # [SYNTHETIC] Plausible ground truths for a fictional annual report corpus.
    "Total revenue for the fiscal year was approximately $4.2 billion, representing a 9% increase over the prior year.",
    "The Enterprise Solutions segment reported the highest operating margin at 28%, driven by software licensing and recurring subscription revenue.",
    "Management identified macroeconomic uncertainty, foreign exchange volatility, increased competition in core markets, and cybersecurity risk as primary risk factors.",
    "Total headcount grew from 12,400 to 13,100 employees, a net addition of 700 full-time equivalents, primarily in engineering and customer success roles.",
    "The company completed construction of a new data center in Virginia and announced a $300 million expansion of its Asia-Pacific manufacturing facility.",
    "The board approved a $500 million share repurchase program and declared a quarterly dividend of $0.18 per share, up from $0.15 in the prior year.",
    "The executive leadership team includes the Chief Executive Officer, Chief Financial Officer, Chief Technology Officer, Chief Operating Officer, and Chief People Officer.",
    "Latin America and Southeast Asia showed the strongest revenue growth at 18% and 22% year-over-year respectively, outpacing the company's overall growth rate.",
]
