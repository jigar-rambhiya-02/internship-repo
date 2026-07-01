# Text-to-SQL BI Co-Pilot

## File Structure

```
text2sql/
├── config/
│   └── settings.py           # Env var loading, constants, fail-fast checks
├── src/
│   ├── utils/
│   │   └── logger.py         # Dual-sink logger (stdout + output.log)
│   ├── schema_loader.py      # BQ client, schema fetch, sample values
│   ├── sql_validator.py      # dry_run_query, retry_sql_generation
│   ├── agent.py              # Orchestrator: run_pipeline, generate_sql, execute_query
│   ├── summarizer.py         # NL summary via Groq
│   └── chart_picker.py       # Chart type selection + matplotlib rendering
├── tests/
│   └── test_queries.py       # 15 NL queries (easy/medium/hard), batch runner
├── test_results/             # Auto-created; one subfolder per query run
│   └── query_1/
│       ├── nl_question.txt
│       ├── generated_sql.sql
│       ├── validation_status.txt
│       ├── result_table.csv
│       ├── nl_summary.txt
│       ├── chart.png
│       └── success.txt  (or failure.txt)
├── myenv/                    # Virtual environment (created by setup.sh)
├── setup.sh                  # One-shot directory + file scaffold script
├── requirements.txt          # Python dependencies with version pins
├── output.log                # Appended structured logs from all runs
├── README.md                 # Blank; intern fills in
├── dataset_choice.md         # Dataset rationale (intern fills in)
├── test_queries.md           # 15 NL queries listed (intern fills in)
├── learnings.md              # Post-run reflections (intern fills in)
└── questions.md              # Viva questions

```