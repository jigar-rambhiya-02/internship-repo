self_repair/
├── repair_loop.py        # Core retry + validation logic
├── schema.py             # Pydantic models for ContactCard
├── run_experiment.py     # Loads inputs, runs loop, writes CSV
├── inputs/
│   ├── input_01.txt
│   ├── input_02.txt
│   └── ... (20 files)
├── results.csv           # Auto-generated after running
├── comparison.md         # You write this after the experiment
├── .env                  # Template for environment variables
├── requirements.txt      # Python dependencies
└── README.md             # Project overview
