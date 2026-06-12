"""
query.py - Query the vector search index with optional metadata filters.
Supports pure vector search and RAG mode (with Groq LLM for answer synthesis).
"""

import os
import sys
import json
import argparse
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "arxiv_papers"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 5

# ── Groq LLM ───────────────────────────────────────────────────────────────

def get_groq_client():
    """Initialize Groq client if API key is available."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except ImportError:
        print("⚠ groq package not installed. RAG mode disabled.")
        return None


def synthesize_answer(question: str, chunks: list[dict], groq_client) -> str:
    """Use Groq LLM to synthesize an answer from retrieved chunks."""
    # Build context from chunks
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        source = f"[{meta.get('title', 'Unknown')} | {meta.get('year', '?')} | p.{meta.get('page_number', '?')}]"
        context_parts.append(f"--- Chunk {i} {source} ---\n{chunk['text']}")

    context = "\n\n".join(context_parts)

    prompt = f"""You are a research assistant. Answer the question based ONLY on the provided context chunks from academic papers. 
If the context doesn't contain enough information, say so. Cite the source papers when possible.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024,
    )

    return response.choices[0].message.content


# ── Vector Search ───────────────────────────────────────────────────────────

from typing import Optional

def build_where_filter(year: str = None, doc_type: str = None,
                       doc_id: str = None) -> Optional[dict]:
    """Build ChromaDB where filter from optional metadata constraints."""
    conditions = []

    if year:
        conditions.append({"year": {"$eq": year}})
    if doc_type:
        conditions.append({"doc_type": {"$eq": doc_type}})
    if doc_id:
        conditions.append({"doc_id": {"$eq": doc_id}})

    if not conditions:
        return None
    elif len(conditions) == 1:
        return conditions[0]
    else:
        return {"$and": conditions}


def search(query: str, collection, embed_model: SentenceTransformer,
           top_k: int = DEFAULT_TOP_K, year: str = None,
           doc_type: str = None, doc_id: str = None) -> list[dict]:
    """
    Perform vector search with optional metadata filters.
    Returns list of {text, metadata, distance} dicts.
    """
    # Embed the query
    query_embedding = embed_model.encode([query])[0].tolist()

    # Build filter
    where_filter = build_where_filter(year=year, doc_type=doc_type, doc_id=doc_id)

    # Query ChromaDB
    kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }
    if where_filter:
        kwargs["where"] = where_filter

    try:
        results = collection.query(**kwargs)
    except Exception as e:
        print(f"⚠ Query error: {e}")
        return []

    # Format results
    formatted = []
    if results and results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            formatted.append({
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "similarity": 1 - results["distances"][0][i],  # cosine: 1 - distance
            })

    return formatted


def format_results(results: list[dict], show_text: bool = True) -> str:
    """Format search results for display."""
    if not results:
        return "  No results found."

    lines = []
    for i, r in enumerate(results, 1):
        meta = r["metadata"]
        sim = r["similarity"]
        lines.append(f"  {'─'*56}")
        lines.append(f"  📌 Result {i} | Similarity: {sim:.4f}")
        lines.append(f"     Doc:  {meta.get('title', 'Unknown')[:80]}")
        lines.append(f"     ID:   {meta.get('doc_id', '?')} | Year: {meta.get('year', '?')} | "
                     f"Type: {meta.get('doc_type', '?')} | Page: {meta.get('page_number', '?')}")
        if show_text:
            text_preview = r["text"][:300].replace("\n", " ")
            lines.append(f"     Text: {text_preview}...")
    lines.append(f"  {'─'*56}")
    return "\n".join(lines)


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Query the vector search index with optional filters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python query.py "What is attention mechanism?"
  python query.py "transformer architecture" --top_k 10
  python query.py "reinforcement learning" --year 2024
  python query.py "NLP preprocessing" --doc_type cs.CL --rag
        """,
    )
    parser.add_argument("question", type=str, help="Natural language query")
    parser.add_argument("--top_k", type=int, default=DEFAULT_TOP_K,
                       help="Number of results to return (default: 5)")
    parser.add_argument("--year", type=str, default=None,
                       help="Filter by year (e.g., 2023)")
    parser.add_argument("--doc_type", type=str, default=None,
                       help="Filter by doc type / arXiv category (e.g., cs.CL)")
    parser.add_argument("--doc_id", type=str, default=None,
                       help="Filter by specific document ID")
    parser.add_argument("--rag", action="store_true",
                       help="Enable RAG mode: synthesize answer using Groq LLM")
    parser.add_argument("--no_text", action="store_true",
                       help="Don't show chunk text in results")
    parser.add_argument("--json", action="store_true",
                       help="Output results as JSON")

    args = parser.parse_args()

    # Initialize ChromaDB
    if not CHROMA_DIR.exists():
        print("❌ ChromaDB not found. Run ingest.py first!")
        sys.exit(1)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        print(f"❌ Collection '{COLLECTION_NAME}' not found. Run ingest.py first!")
        sys.exit(1)

    # Load embedding model
    print(f"🤖 Loading embedding model: {EMBEDDING_MODEL}")
    embed_model = SentenceTransformer(EMBEDDING_MODEL)

    # Build filter description
    filters_desc = []
    if args.year:
        filters_desc.append(f"year={args.year}")
    if args.doc_type:
        filters_desc.append(f"doc_type={args.doc_type}")
    if args.doc_id:
        filters_desc.append(f"doc_id={args.doc_id}")
    filter_str = ", ".join(filters_desc) if filters_desc else "none"

    print(f"\n🔍 Query: \"{args.question}\"")
    print(f"   Filters: {filter_str}")
    print(f"   Top-K: {args.top_k}")

    # Search
    results = search(
        query=args.question,
        collection=collection,
        embed_model=embed_model,
        top_k=args.top_k,
        year=args.year,
        doc_type=args.doc_type,
        doc_id=args.doc_id,
    )

    if args.json:
        # JSON output
        output = {
            "query": args.question,
            "filters": {"year": args.year, "doc_type": args.doc_type, "doc_id": args.doc_id},
            "top_k": args.top_k,
            "num_results": len(results),
            "results": results,
        }
        print(json.dumps(output, indent=2))
    else:
        # Formatted output
        print(f"\n📊 Results ({len(results)} found):\n")
        print(format_results(results, show_text=not args.no_text))

    # RAG mode
    if args.rag and results:
        groq_client = get_groq_client()
        if groq_client:
            print(f"\n{'='*60}")
            print("🧠 RAG Answer (powered by Groq + Llama 3.3 70B):")
            print(f"{'='*60}\n")
            answer = synthesize_answer(args.question, results, groq_client)
            print(answer)
            print(f"\n{'='*60}")
        else:
            print("\n⚠ RAG mode requires GROQ_API_KEY in .env")

    return results


if __name__ == "__main__":
    main()
