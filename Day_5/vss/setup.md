# Vector Search System (VSS) — Setup Guide

## Overview

A production-style vector search index built over **200+ arXiv ML/AI papers**, enabling semantic search with metadata filtering and optional RAG (Retrieval-Augmented Generation) via Groq.

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌───────────┐
│  arXiv PDFs │ ──▶ │  pypdf Parse │ ──▶ │ 512-token Chunk │ ──▶ │  Embed    │
│  (200+)     │     │  + Extract   │     │ + 50 overlap    │     │ MiniLM-L6 │
└─────────────┘     └──────────────┘     └─────────────────┘     └─────┬─────┘
                                                                       │
                                                                       ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────────────────────────┐
│  Groq LLM   │ ◀── │  query.py    │ ◀── │  ChromaDB (persistent, cosine)     │
│  (RAG mode) │     │  + filters   │     │  384-dim vectors + metadata        │
└─────────────┘     └──────────────┘     └─────────────────────────────────────┘
```

---

## Index Configuration

| Parameter | Value |
|---|---|
| **Embedding Model** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Embedding Dimensions** | 384 |
| **Distance Metric** | Cosine similarity (`hnsw:space = cosine`) |
| **Chunk Size** | 512 tokens |
| **Chunk Overlap** | 50 tokens |
| **Tokenizer** | `tiktoken` (`cl100k_base` encoding) |
| **Vector Database** | ChromaDB (persistent local storage) |
| **Collection Name** | `arxiv_papers` |
| **LLM (RAG mode)** | Groq `llama-3.3-70b-versatile` |

---

## Prerequisites

- Python 3.10+
- ~2 GB disk space for embeddings + model weights
- Groq API key (optional, for RAG mode)

---

## Installation

```bash
# Navigate to project directory
cd Tasks/Day_5/vss/

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

---

## Setup

1. **Environment Variables**: Create a `.env` file:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

2. **Download Corpus** (200+ arXiv papers):
   ```bash
   python download_corpus.py
   ```
   This downloads ~210 ML/AI papers into `./corpus/` and saves metadata to `corpus_metadata.json`.

3. **Run Ingestion Pipeline**:
   ```bash
   python ingest.py
   ```
   This parses all PDFs, chunks them, generates embeddings, and stores everything in ChromaDB at `./chroma_db/`. Also generates `corpus_manifest.csv`.

---

## Usage

### Basic Query
```bash
python query.py "What is the transformer architecture?"
```

### With Metadata Filters
```bash
# Filter by year
python query.py "reinforcement learning" --year 2024

# Filter by document type (arXiv category)
python query.py "image generation" --doc_type cs.CV

# Multiple filters
python query.py "NLP preprocessing" --doc_type cs.CL --top_k 10
```

### RAG Mode (with Groq LLM)
```bash
python query.py "How does attention work?" --rag
```

### JSON Output
```bash
python query.py "gradient descent" --json
```

### Generate Filtered Queries Report
```bash
python run_queries.py
```

---

## Metadata Filters

The following metadata fields are stored per chunk and can be used as filters:

| Field | Description | Example |
|---|---|---|
| `doc_id` | arXiv paper ID | `2301.12345` |
| `year` | Publication year | `2024` |
| `doc_type` | Primary arXiv category | `cs.LG`, `cs.CV`, `cs.CL`, `cs.AI` |
| `page_number` | Source page in PDF | `5` |
| `title` | Paper title | `Attention Is All You Need` |
| `chunk_index` | Chunk position in document | `12` |

---

## File Structure

```
vss/
├── .env                    # API keys
├── requirements.txt        # Python dependencies
├── download_corpus.py      # Download arXiv PDFs
├── ingest.py               # Parse → Chunk → Embed → Index
├── query.py                # Query with filters + RAG
├── run_queries.py          # Generate 10 example queries report
├── setup.md                # This file
├── corpus_manifest.csv     # Index of all documents
├── filtered_queries.md     # 10 example query results
├── corpus/                 # Downloaded PDFs (200+)
├── corpus_metadata.json    # arXiv metadata for papers
└── chroma_db/              # Persistent ChromaDB storage
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `No PDFs found` | Run `python download_corpus.py` first |
| `Collection not found` | Run `python ingest.py` first |
| `RAG not working` | Check `GROQ_API_KEY` in `.env` |
| `Out of memory` | Reduce `BATCH_SIZE` in `ingest.py` (default: 100) |
| `Slow embedding` | Expected ~5 min for 200+ papers on CPU |
