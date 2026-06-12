"""
run_queries.py - Run 10 example queries with metadata filters and save results to filtered_queries.md
"""

import os
import sys
from pathlib import Path
from datetime import datetime

import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Import search function from query module
sys.path.insert(0, str(Path(__file__).parent))
from query import search, get_groq_client, synthesize_answer

load_dotenv()

BASE_DIR = Path(__file__).parent
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "arxiv_papers"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OUTPUT_FILE = BASE_DIR / "filtered_queries.md"

# ── 10 Example Queries with Filters ────────────────────────────────────────

EXAMPLE_QUERIES = [
    {
        "question": "What is the transformer architecture and how does self-attention work?",
        "filters": {},
        "description": "Broad semantic search — no filters",
    },
    {
        "question": "How does reinforcement learning from human feedback improve language models?",
        "filters": {"doc_type": "cs.CL"},
        "description": "Filter by NLP/Computation & Language papers",
    },
    {
        "question": "What are the latest advances in diffusion models for image generation?",
        "filters": {"doc_type": "cs.CV"},
        "description": "Filter by Computer Vision papers",
    },
    {
        "question": "Explain gradient descent optimization techniques for deep learning",
        "filters": {"doc_type": "cs.LG"},
        "description": "Filter by Machine Learning papers",
    },
    {
        "question": "What is contrastive learning and how is it used in self-supervised learning?",
        "filters": {},
        "description": "Broad search across all categories",
    },
    {
        "question": "How do graph neural networks capture structural information?",
        "filters": {"doc_type": "cs.LG"},
        "description": "Filter by Machine Learning category",
    },
    {
        "question": "What are the challenges of training large language models at scale?",
        "filters": {"doc_type": "cs.CL"},
        "description": "Filter by NLP papers only",
    },
    {
        "question": "How does knowledge distillation compress neural networks?",
        "filters": {"doc_type": "cs.AI"},
        "description": "Filter by AI papers",
    },
    {
        "question": "What methods exist for explainability and interpretability of neural networks?",
        "filters": {},
        "description": "Broad search — interpretability across domains",
    },
    {
        "question": "How do vision transformers compare to convolutional neural networks?",
        "filters": {"doc_type": "cs.CV"},
        "description": "Filter by Computer Vision papers",
    },
]


def format_chunk_for_md(i: int, result: dict) -> str:
    """Format a single result chunk as markdown."""
    meta = result["metadata"]
    sim = result["similarity"]
    text_preview = result["text"][:400].replace("\n", " ").strip()

    return f"""   **Chunk {i}** — Similarity: `{sim:.4f}`
   - **Doc:** {meta.get('title', 'Unknown')[:90]}
   - **ID:** `{meta.get('doc_id', '?')}` | **Year:** {meta.get('year', '?')} | **Type:** `{meta.get('doc_type', '?')}` | **Page:** {meta.get('page_number', '?')}
   - **Text:** _{text_preview}_
"""


def main():
    # Initialize
    print("🔍 Running 10 example queries for filtered_queries.md...\n")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(COLLECTION_NAME)
    embed_model = SentenceTransformer(EMBEDDING_MODEL)

    # Check collection size
    count = collection.count()
    print(f"📊 Collection has {count} chunks indexed\n")

    groq_client = get_groq_client()

    # Build markdown
    md_lines = [
        "# Filtered Queries — Vector Search Results\n",
        f"> Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> Collection: `{COLLECTION_NAME}` | Chunks indexed: **{count}**",
        f"> Embedding model: `{EMBEDDING_MODEL}` (384-dim) | Distance: cosine\n",
        "---\n",
    ]

    for qi, q in enumerate(EXAMPLE_QUERIES, 1):
        question = q["question"]
        filters = q["filters"]
        desc = q["description"]

        print(f"  [{qi}/10] {question[:60]}...")

        results = search(
            query=question,
            collection=collection,
            embed_model=embed_model,
            top_k=5,
            year=filters.get("year"),
            doc_type=filters.get("doc_type"),
            doc_id=filters.get("doc_id"),
        )

        # Format filter string
        if filters:
            filter_str = ", ".join(f"`{k}={v}`" for k, v in filters.items())
        else:
            filter_str = "None (all documents)"

        md_lines.append(f"## Query {qi}: {question}\n")
        md_lines.append(f"- **Filters:** {filter_str}")
        md_lines.append(f"- **Description:** {desc}")
        md_lines.append(f"- **Results returned:** {len(results)}\n")

        if results:
            md_lines.append("### Top-5 Retrieved Chunks\n")
            for i, r in enumerate(results, 1):
                md_lines.append(format_chunk_for_md(i, r))
        else:
            md_lines.append("_No results found for this query with the given filters._\n")

        # Add RAG answer if Groq is available
        if groq_client and results:
            try:
                answer = synthesize_answer(question, results, groq_client)
                md_lines.append("### 🧠 RAG-Synthesized Answer\n")
                md_lines.append(f"> {answer}\n")
            except Exception as e:
                md_lines.append(f"_RAG answer failed: {e}_\n")

        md_lines.append("---\n")

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"\n✅ Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
