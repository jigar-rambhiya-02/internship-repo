```
day5_vector_search/
├── vvs/
│   ├── ingest.py
│   ├── query.py
│   ├── corpus_manifest.csv        # auto-generated, starts empty
│   ├── filtered_queries.md        # filled after testing
│   └── setup.md                   # Vertex AI config reference
├── src/
│   ├── __init__.py
│   ├── pdf_parser.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── vector_store.py
│   └── groq_synthesizer.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── utils/
│   ├── __init__.py
│   └── logger.py
├── tests/
│   ├── __init__.py
│   ├── test_chunker.py
│   ├── test_embedder.py
│   └── test_query.py
├── data/
│   └── pdfs/                      # raw downloaded PDFs land here
├── logs/
│   └── .gitkeep
├── output.log                     # auto-created by logger
├── .env
├── .gitignore
├── requirements.txt
├── setup.sh
└── README.md

```