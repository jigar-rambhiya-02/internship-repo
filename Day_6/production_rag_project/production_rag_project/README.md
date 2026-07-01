```
production_rag_project/
├── myenv/                          # Virtual environment (git-ignored)
├── data/
│   └── corpus.pdf                  # Default sample corpus document
├── production_rag/
│   ├── __init__.py
│   ├── reranker.py                 # Re-ranker wrapper (Vertex AI + fallback)
│   ├── contextualizer.py           # Context prefix generator + re-indexer
│   ├── retriever.py                # Base embedding retriever (ChromaDB)
│   ├── generator.py                # Groq LLM answer generator
│   ├── evaluator.py                # RAGAS eval harness (4 configurations)
│   ├── pipeline.py                 # Orchestrates full RAG pipeline per config
│   └── results.csv                 # Output: eval scores across all configs (auto-created)
├── config/
│   ├── __init__.py
│   └── settings.py                 # Centralized config (model names, top-k values, paths)
├── utils/
│   ├── __init__.py
│   ├── logger.py                   # Structured logger (file + console dual output)
│   ├── pdf_loader.py               # PDF chunking utility
│   └── chroma_store.py             # ChromaDB init + collection management
├── tests/
│   ├── __init__.py
│   ├── test_reranker.py
│   ├── test_contextualizer.py
│   └── test_evaluator.py
├── lift_report.md                  # Auto-generated lift analysis (fill after eval run)
├── output.log                      # Runtime log (auto-created, git-ignored)
├── questions.md                    # Intern viva questions
├── .env                            # API keys (git-ignored)
├── .gitignore
├── requirements.txt
└── README.md
```