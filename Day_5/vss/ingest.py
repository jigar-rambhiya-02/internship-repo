"""
ingest.py - Parse, chunk, embed, and index PDFs into ChromaDB
Production-style ingestion pipeline for vector search.
"""

import os
import sys
import json
import csv
import hashlib
from pathlib import Path

import tiktoken
import chromadb
from chromadb.config import Settings
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
CORPUS_DIR = BASE_DIR / "corpus"
CHROMA_DIR = BASE_DIR / "chroma_db"
METADATA_FILE = BASE_DIR / "corpus_metadata.json"
MANIFEST_FILE = BASE_DIR / "corpus_manifest.csv"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
COLLECTION_NAME = "arxiv_papers"
CHUNK_SIZE = 512        # tokens
CHUNK_OVERLAP = 50      # tokens
BATCH_SIZE = 100        # ChromaDB insertion batch size

# ── Tokenizer ───────────────────────────────────────────────────────────────

def get_tokenizer():
    """Get tiktoken tokenizer for chunking."""
    return tiktoken.get_encoding("cl100k_base")


# ── PDF Parsing ─────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: Path) -> list[dict]:
    """
    Extract text from a PDF, returning a list of {page_number, text} dicts.
    """
    pages = []
    try:
        reader = PdfReader(str(pdf_path))
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append({
                    "page_number": i + 1,
                    "text": text.strip(),
                })
    except Exception as e:
        print(f"  ⚠ Error reading {pdf_path.name}: {e}")
    return pages


# ── Chunking ────────────────────────────────────────────────────────────────

def chunk_text(text: str, tokenizer, chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into chunks of `chunk_size` tokens with `overlap` token overlap.
    """
    tokens = tokenizer.encode(text)
    chunks = []

    if len(tokens) <= chunk_size:
        return [text]

    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text_str = tokenizer.decode(chunk_tokens)
        if chunk_text_str.strip():
            chunks.append(chunk_text_str.strip())

        if end >= len(tokens):
            break
        start += chunk_size - overlap

    return chunks


# ── Document Processing ────────────────────────────────────────────────────

def process_document(pdf_path: Path, doc_metadata: dict, tokenizer) -> list[dict]:
    """
    Process a single PDF: extract text, chunk, prepare for embedding.
    Returns list of chunk dicts ready for embedding.
    """
    pages = extract_text_from_pdf(pdf_path)
    if not pages:
        return []

    doc_id = doc_metadata.get("arxiv_id", pdf_path.stem)
    title = doc_metadata.get("title", pdf_path.stem)
    year = doc_metadata.get("year", "unknown")
    categories = doc_metadata.get("categories", [])
    doc_type = categories[0] if categories else "cs.LG"

    all_chunks = []
    chunk_index = 0

    for page_data in pages:
        page_text = page_data["text"]
        page_num = page_data["page_number"]

        chunks = chunk_text(page_text, tokenizer)

        for chunk_str in chunks:
            chunk_id = hashlib.md5(
                f"{doc_id}_{page_num}_{chunk_index}".encode()
            ).hexdigest()

            all_chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_str,
                "metadata": {
                    "doc_id": doc_id,
                    "title": title,
                    "year": year,
                    "doc_type": doc_type,
                    "page_number": page_num,
                    "chunk_index": chunk_index,
                },
            })
            chunk_index += 1

    return all_chunks


# ── Embedding ───────────────────────────────────────────────────────────────

def embed_chunks(chunks: list[dict], model: SentenceTransformer) -> list[dict]:
    """Add embeddings to chunk dicts."""
    texts = [c["text"] for c in chunks]
    if not texts:
        return chunks

    embeddings = model.encode(texts, show_progress_bar=False, batch_size=64)

    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i].tolist()

    return chunks


# ── ChromaDB Storage ────────────────────────────────────────────────────────

def store_in_chromadb(chunks: list[dict], collection):
    """Store embedded chunks into ChromaDB collection in batches."""
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]

        ids = [c["chunk_id"] for c in batch]
        documents = [c["text"] for c in batch]
        embeddings = [c["embedding"] for c in batch]
        metadatas = [c["metadata"] for c in batch]

        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )


# ── Manifest Generation ────────────────────────────────────────────────────

def generate_manifest(doc_stats: list[dict]):
    """Generate corpus_manifest.csv from document statistics."""
    with open(MANIFEST_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "doc_id", "title", "year", "doc_type", "num_pages", "num_chunks"
        ])
        writer.writeheader()
        for doc in sorted(doc_stats, key=lambda x: x["doc_id"]):
            writer.writerow(doc)

    print(f"📄 Manifest saved: {MANIFEST_FILE}")


# ── Main Pipeline ───────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🚀 Vector Search Ingestion Pipeline")
    print("=" * 60)

    # Validate corpus
    if not CORPUS_DIR.exists():
        print(f"❌ Corpus directory not found: {CORPUS_DIR}")
        print("   Run download_corpus.py first!")
        sys.exit(1)

    pdf_files = sorted(CORPUS_DIR.glob("*.pdf"))
    if len(pdf_files) == 0:
        print("❌ No PDF files found in corpus/")
        print("   Run download_corpus.py first!")
        sys.exit(1)

    print(f"📚 Found {len(pdf_files)} PDFs in {CORPUS_DIR}")

    # Load arXiv metadata
    arxiv_metadata = {}
    if METADATA_FILE.exists():
        with open(METADATA_FILE, "r") as f:
            meta_list = json.load(f)
            for m in meta_list:
                # Map local filename (without extension) to metadata
                if "local_filename" in m:
                    key = m["local_filename"].replace(".pdf", "")
                    arxiv_metadata[key] = m
                # Also map by arxiv_id (with dots replaced)
                safe_id = m["arxiv_id"].replace("/", "_").replace(".", "_")
                arxiv_metadata[safe_id] = m

    # Initialize embedding model
    print(f"\n🤖 Loading embedding model: {EMBEDDING_MODEL}")
    embed_model = SentenceTransformer(EMBEDDING_MODEL)

    # Initialize ChromaDB
    print(f"💾 Initializing ChromaDB at: {CHROMA_DIR}")
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Delete existing collection if re-running
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"   ♻ Cleared existing collection: {COLLECTION_NAME}")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine similarity
    )

    # Initialize tokenizer
    tokenizer = get_tokenizer()

    # Process all documents
    doc_stats = []
    total_chunks = 0
    failed_docs = 0

    print(f"\n📖 Processing {len(pdf_files)} documents...\n")

    for pdf_path in tqdm(pdf_files, desc="Ingesting PDFs"):
        # Get metadata for this PDF
        stem = pdf_path.stem
        doc_meta = arxiv_metadata.get(stem, {
            "arxiv_id": stem,
            "title": stem,
            "year": "unknown",
            "categories": ["cs.LG"],
        })

        # Process: parse → chunk → embed
        chunks = process_document(pdf_path, doc_meta, tokenizer)

        if not chunks:
            failed_docs += 1
            continue

        # Embed chunks
        chunks = embed_chunks(chunks, embed_model)

        # Store in ChromaDB
        store_in_chromadb(chunks, collection)

        # Track stats
        pages = extract_text_from_pdf(pdf_path)
        doc_stats.append({
            "doc_id": doc_meta.get("arxiv_id", stem),
            "title": doc_meta.get("title", stem)[:100],
            "year": doc_meta.get("year", "unknown"),
            "doc_type": doc_meta.get("categories", ["cs.LG"])[0] if doc_meta.get("categories") else "cs.LG",
            "num_pages": len(pages),
            "num_chunks": len(chunks),
        })
        total_chunks += len(chunks)

    # Generate manifest
    generate_manifest(doc_stats)

    # Summary
    print(f"\n{'='*60}")
    print(f"✅ Ingestion Complete!")
    print(f"   Documents processed: {len(doc_stats)}")
    print(f"   Documents failed:    {failed_docs}")
    print(f"   Total chunks:        {total_chunks}")
    print(f"   Embedding model:     {EMBEDDING_MODEL} ({EMBEDDING_DIM}-dim)")
    print(f"   Distance metric:     cosine")
    print(f"   Chunk size:          {CHUNK_SIZE} tokens")
    print(f"   Chunk overlap:       {CHUNK_OVERLAP} tokens")
    print(f"   ChromaDB path:       {CHROMA_DIR}")
    print(f"   Manifest:            {MANIFEST_FILE}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
