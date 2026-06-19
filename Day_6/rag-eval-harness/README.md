```
rag-eval-harness/
├── myenv/
├── data/
│   └── raw/                  # Intern drops .txt corpus files here
├── src/
│   ├── __init__.py
│   ├── ingest.py             # Chunking + ChromaDB indexing pipeline
│   ├── rag_bot.py            # RAG retrieval + generation logic
│   └── utils.py              # Shared utilities (logging setup, token counting)
├── eval/
│   ├── test_set.jsonl        # 30 questions with ground-truth answers + chunk_ids
│   ├── judges.py             # 4 judge functions (one per metric)
│   ├── run_eval.py           # Master evaluation orchestrator
│   ├── results.csv           # Auto-generated: scores for all 30 questions
│   └── eval_report.md        # Auto-generated: aggregate analysis + best/worst cases
├── tests/
│   ├── test_judges.py
│   └── test_rag_bot.py
├── config/
│   └── settings.py           # Central config: model names, chunk size, top_k, thresholds
├── .env                      # GROQ_API_KEY lives here (never commit this)
├── .gitignore
├── requirements.txt
├── output.log                # Auto-created: all logs mirrored here
└── guide.md
```