# Data Engineer — 10 Tasks (Beginner → 2‑Year Experience)

> **Goal:** Go from "I know Python and SQL" to "I can design, build, and operate reliable data pipelines that feed ML models and analytics at scale."
> A Data Engineer builds the infrastructure and pipelines that make data available, clean, and timely — without you, data scientists have nothing to work with.
> Each task is self‑contained. Difficulty increases from Task 1 → 10.

---

## Task 1: Data Formats & Serialisation — CSV, JSON, Parquet & Avro

**Difficulty:** ⭐ Beginner

**What you'll learn:**
- Row‑oriented vs columnar storage formats
- When to use CSV, JSON, Parquet, and Avro
- Compression: gzip, snappy, zstd — trade‑offs
- Schema evolution: what happens when columns are added/removed

**What to read first:**
- 📖 [Apache Parquet Documentation](https://parquet.apache.org/documentation/latest/) (overview)
- 📖 [Databricks: Parquet vs CSV](https://www.databricks.com/glossary/what-is-parquet) (5 min)
- 📖 [Apache Avro Getting Started](https://avro.apache.org/docs/current/getting-started-python/) (Python)
- 📖 [DuckDB: Reading Various File Formats](https://duckdb.org/docs/data/overview.html)

**Task:**
1. Take a medium‑sized dataset (~100K rows): [NYC Taxi Trip Data (sample)](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) or [Kaggle Online Retail](https://www.kaggle.com/datasets/carrie1/ecommerce-data).
2. Write `format_benchmark.py` that:
   - Saves the dataset in 4 formats: CSV, JSON Lines, Parquet, Parquet+snappy compression
   - Measures and records: file size, write time, read time for each format
   - Reads back each format and verifies row count + schema match
   - Runs a simple query ("total revenue by country") on each format using DuckDB and times it
3. Write `schema_evolution.py`:
   - Save a Parquet file with columns [A, B, C]
   - Create new data with columns [A, B, C, D] — save as Parquet
   - Read both files together — show how Parquet handles the missing column (fills with null)
   - Try the same with CSV — show the difference
4. Write `format_guide.md`:
   - Comparison table: format, size, read speed, write speed, schema support, human readable, streaming support
   - Decision tree: "When should I use which format?"

**Deliverables:**
1. `/data_engineer/task1/format_benchmark.py`
2. `/data_engineer/task1/schema_evolution.py`
3. `/data_engineer/task1/format_guide.md` — comparison table + decision tree
4. `/data_engineer/task1/benchmark_results.csv` — timing and size results
5. `/data_engineer/task1/requirements.txt`

---

## Task 2: SQL Mastery — Advanced Queries, CTEs & Window Functions

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- Common Table Expressions (CTEs) for readable queries
- Window functions: ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, NTILE
- Running totals, moving averages, and cumulative distributions
- Query optimisation basics: EXPLAIN, indexing, avoiding full scans

**What to read first:**
- 📖 [Mode Analytics: SQL Window Functions](https://mode.com/sql-tutorial/sql-window-functions/) (excellent tutorial)
- 📖 [Use The Index, Luke](https://use-the-index-luke.com/) — SQL indexing explained visually
- 📖 [DuckDB SQL Reference](https://duckdb.org/docs/sql/introduction.html) (modern SQL)
- 📖 [SQLite EXPLAIN](https://www.sqlite.org/eqp.html) — understanding query plans

**Task:**
1. Load a multi‑table dataset into DuckDB or SQLite: create `orders`, `customers`, `products`, `order_items` tables from [Olist Brazilian E‑Commerce](https://www.kaggle.com/olistbr/brazilian-ecommerce) or generate synthetic relational data.
2. Write `advanced_queries.sql` with 12 queries:
   - CTE: revenue by customer, then filter to top 10% (nested CTE)
   - Window: rank products by revenue within each category (RANK + PARTITION BY)
   - Window: month‑over‑month revenue growth (LAG)
   - Window: 3‑month moving average of daily orders
   - Window: cumulative revenue (running total)
   - Subquery: customers who bought in the first month but not the second (churn)
   - Self‑join: products frequently bought together (co‑purchase analysis)
   - CASE + aggregation: segment customers as "High/Medium/Low" value
   - HAVING: categories with more than 100 orders but average rating < 3.5
   - EXPLAIN on 2 queries — show the query plan, add an index, show the improved plan
   - Recursive CTE (bonus): generate a date dimension table
   - PIVOT‑style query: revenue by month (columns) per product category (rows)
3. Write `run_sql.py` that creates the database, runs all queries, and exports results.
4. Write `sql_performance.md`:
   - Before/after EXPLAIN for the indexed queries
   - Rules of thumb: when to use CTEs vs subqueries vs temp tables

**Deliverables:**
1. `/data_engineer/task2/advanced_queries.sql` — 12 queries with comments
2. `/data_engineer/task2/run_sql.py`
3. `/data_engineer/task2/sql_performance.md` — EXPLAIN analysis + indexing advice
4. `/data_engineer/task2/query_results/` — CSV outputs
5. `/data_engineer/task2/requirements.txt`

---

## Task 3: Build an ETL Pipeline — Extract, Transform, Load

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- ETL vs ELT: when to use each
- Extracting data from APIs and files
- Transforming: cleaning, joining, aggregating
- Loading into a local data warehouse (DuckDB / SQLite)
- Idempotent pipelines: safe to re‑run

**What to read first:**
- 📖 [Data Engineering Handbook (GitHub)](https://github.com/DataExpert-io/data-engineer-handbook) — curated resources
- 📖 [DuckDB as a Data Warehouse](https://duckdb.org/why_duckdb.html) (why it works locally)
- 📖 [Python Requests Library](https://requests.readthedocs.io/en/latest/) (for API extraction)
- 📖 [Pandas: Merge, Join, Concatenate](https://pandas.pydata.org/docs/user_guide/merging.html)

**Task:**
1. Build an ETL pipeline that processes data from 3 sources:
   - **Source 1 (API)**: Fetch data from a free public API (e.g., [Open‑Meteo Weather API](https://open-meteo.com/en/docs), [JSONPlaceholder](https://jsonplaceholder.typicode.com/), or [PokéAPI](https://pokeapi.co/))
   - **Source 2 (CSV)**: A local CSV file (e.g., a customer or product list)
   - **Source 3 (JSON Lines)**: A JSONL file (e.g., event log data you simulate)
2. Write `extract.py`:
   - Fetches data from the API (with retry logic and error handling)
   - Reads the CSV and JSONL files
   - Validates that data was extracted: row counts, schema checks
   - Saves raw data to `data/raw/` with timestamps
3. Write `transform.py`:
   - Cleans each source: handle nulls, standardise column names (snake_case), fix types
   - Joins the 3 sources on a common key (or create a meaningful enrichment)
   - Creates 3 aggregate tables (e.g., daily_summary, category_metrics, top_performers)
   - Saves to `data/transformed/`
4. Write `load.py`:
   - Creates a DuckDB database (`warehouse.duckdb`)
   - Creates tables with proper types and constraints
   - Loads transformed data — **idempotent**: uses UPSERT or "drop and recreate" strategy
   - Runs 3 verification queries to confirm data loaded correctly
5. Write `run_pipeline.py` — orchestrates extract → transform → load with logging and timing.

**Deliverables:**
1. `/data_engineer/task3/extract.py`, `transform.py`, `load.py`, `run_pipeline.py`
2. `/data_engineer/task3/pipeline_architecture.md` — diagram + description
3. `/data_engineer/task3/data_catalog.md` — table: source, columns, types, refresh frequency
4. `/data_engineer/task3/requirements.txt`

---

## Task 4: Workflow Orchestration with Airflow (or Prefect)

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- DAGs (Directed Acyclic Graphs): modelling task dependencies
- Scheduling: cron expressions, catchup, backfill
- Task retries, timeouts, and SLAs
- Sensors: waiting for external conditions
- Local development and testing of DAGs

**What to read first:**
- 📖 [Apache Airflow Tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html) (official — first 3 sections)
- 📖 [Astronomer: Airflow Concepts](https://www.astronomer.io/docs/learn/category/airflow-concepts/) (excellent guides)
- 📖 [Prefect: Getting Started](https://docs.prefect.io/latest/getting-started/quickstart/) (alternative orchestrator)
- 📖 [Marc Lamberti: Airflow Tutorial (YouTube)](https://www.youtube.com/watch?v=K9AnJ9_ZAXE) (practical walkthrough)

**Task:**
1. Install Airflow locally using the standalone setup (`airflow standalone`) or use Prefect if you prefer.
2. Write a DAG (`etl_dag.py`) that orchestrates your Task 3 ETL pipeline:
   - **Task 1**: Extract (run `extract.py`)
   - **Task 2**: Validate raw data (check row counts, schema — fail fast if bad)
   - **Task 3**: Transform (run `transform.py`, depends on Task 1 + 2)
   - **Task 4**: Load (run `load.py`, depends on Task 3)
   - **Task 5**: Run quality checks on loaded data (depends on Task 4)
   - **Task 6**: Send notification (print/log success or failure summary)
3. Configure the DAG:
   - Schedule: daily at 6 AM
   - Retries: 2, with 5‑minute delay
   - Timeout: 30 minutes per task
   - Catchup: disabled
4. Write `test_dag.py` — unit test that:
   - Validates DAG loads without errors
   - Checks task dependencies are correct
   - Tests that the DAG has no cycles
5. Take a screenshot of the Airflow UI showing your DAG and a successful run.

**Deliverables:**
1. `/data_engineer/task4/dags/etl_dag.py`
2. `/data_engineer/task4/test_dag.py` — DAG unit tests
3. `/data_engineer/task4/dag_architecture.md` — Mermaid diagram of task dependencies
4. `/data_engineer/task4/orchestration_notes.md` — Airflow vs Prefect comparison, retry strategies, when to use sensors
5. `/data_engineer/task4/airflow_screenshot.png`

---

## Task 5: Data Quality & Testing with Great Expectations

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Data contracts: defining what "correct" data looks like
- Automated data quality checks: schema, completeness, uniqueness, ranges
- Data profiling and expectation generation
- Integrating data quality into pipelines (fail‑fast)

**What to read first:**
- 📖 [Great Expectations Getting Started](https://docs.greatexpectations.io/docs/tutorials/quickstart/) (30 min)
- 📖 [Soda: Data Quality Concepts](https://www.soda.io/resources/data-quality) (alternative tool, good concepts)
- 📖 [Monte Carlo: Data Observability](https://www.montecarlodata.com/blog-data-observability/) (concepts)
- 📖 [dbt: Tests and Data Quality](https://docs.getdbt.com/docs/build/data-tests) (SQL‑based testing)

**Task:**
1. Take your ETL pipeline data (from Task 3) or any multi‑table dataset.
2. Write `data_expectations.py` using Great Expectations:
   - Define 15+ expectations across your tables:
     - Column existence checks (expect_column_to_exist)
     - Type checks (expect_column_values_to_be_of_type)
     - Null checks (expect_column_values_to_not_be_null)
     - Uniqueness (expect_column_values_to_be_unique)
     - Range checks (expect_column_values_to_be_between)
     - Set membership (expect_column_values_to_be_in_set)
     - Regex pattern (expect_column_values_to_match_regex)
     - Row count bounds (expect_table_row_count_to_be_between)
     - Cross‑column: column A <= column B
   - Run expectations and generate a validation report
3. Write `data_profiler.py`:
   - Profile the dataset: compute min, max, mean, nulls, cardinality, top‑10 values per column
   - Auto‑generate expectations from the profile (e.g., "values are between min and max observed")
   - Save the profile as JSON
4. Write `simulate_bad_data.py`:
   - Generate 5 versions of the data with specific issues: nulls, duplicates, out‑of‑range, wrong types, schema drift
   - Run expectations against each → show which checks catch which issues
5. Write `data_quality_report.md`:
   - Results table: data version × expectation → PASS/FAIL
   - Which expectations caught real issues? Which were too strict?
   - Your data quality checklist for new tables

**Deliverables:**
1. `/data_engineer/task5/data_expectations.py`
2. `/data_engineer/task5/data_profiler.py`
3. `/data_engineer/task5/simulate_bad_data.py`
4. `/data_engineer/task5/data_quality_report.md`
5. `/data_engineer/task5/requirements.txt`

---

## Task 6: Streaming Data Processing — Real‑Time Pipelines

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Batch vs stream processing: when to use each
- Message queues and event streaming concepts
- Building a stream processing pipeline with Python
- Windowing: tumbling, sliding, session windows
- Exactly‑once vs at‑least‑once semantics

**What to read first:**
- 📖 [Apache Kafka: Introduction](https://kafka.apache.org/intro) (concepts)
- 📖 [Redpanda: What is Event Streaming?](https://redpanda.com/guides/kafka-alternatives/event-streaming) (beginner‑friendly)
- 📖 [Bytewax: Real‑Time Data Processing in Python](https://bytewax.io/docs/getting-started/overview) (open‑source, Python‑native)
- 📖 [RabbitMQ Tutorial (Python)](https://www.rabbitmq.com/tutorials/tutorial-one-python.html) (simple queue)

**Task:**
1. Write `event_producer.py`:
   - Simulates a stream of e‑commerce events (page_view, add_to_cart, purchase, search) at ~10 events/second
   - Each event has: timestamp, user_id, event_type, product_id, amount, session_id
   - Writes events to a file‑based queue (one JSON per line, appended to `events.jsonl`) — or use Redis/RabbitMQ if you want a real queue
2. Write `stream_processor.py`:
   - Reads events as they arrive (tail the file, or consume from queue)
   - Computes real‑time aggregations:
     - Events per second (1‑second tumbling window)
     - Revenue per minute (1‑minute tumbling window)
     - Unique users in the last 5 minutes (5‑minute sliding window)
     - Conversion funnel: page_view → add_to_cart → purchase (session‑based)
   - Detects anomalies: alert if events/second drops below 2 or spikes above 50
   - Writes aggregations to `aggregations.jsonl`
3. Write `stream_dashboard.py` (optional but recommended):
   - A simple Streamlit app that shows the real‑time aggregations updating
4. Write `streaming_architecture.md`:
   - Diagram: producer → queue → processor → sink
   - Batch vs stream: comparison table (latency, complexity, cost, use cases)
   - Windowing explained with examples
   - Exactly‑once vs at‑least‑once: when does it matter?

**Deliverables:**
1. `/data_engineer/task6/event_producer.py`
2. `/data_engineer/task6/stream_processor.py`
3. `/data_engineer/task6/stream_dashboard.py` (optional)
4. `/data_engineer/task6/streaming_architecture.md`
5. `/data_engineer/task6/requirements.txt`

---

## Task 7: Data Modelling — Star Schema, Slowly Changing Dimensions & dbt

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- Dimensional modelling: facts vs dimensions, star schema vs snowflake
- Slowly Changing Dimensions (SCD Types 1, 2, 3)
- dbt (data build tool): SQL transformations with testing and documentation
- Data lineage and documentation

**What to read first:**
- 📖 [Kimball Group: Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) (canonical reference)
- 📖 [dbt: Getting Started](https://docs.getdbt.com/docs/introduction) (free, open‑source)
- 📖 [Slowly Changing Dimensions Explained](https://www.sqlshack.com/implementing-slowly-changing-dimensions-scds-in-data-warehouses/) (tutorial)
- 📖 [The Data Warehouse Toolkit — Kimball (summary)](https://www.holistics.io/blog/the-kimball-methodology/) (blog summary)

**Task:**
1. Design a star schema for an e‑commerce data warehouse:
   - **Fact table**: `fct_orders` (order_id, customer_key, product_key, date_key, quantity, amount, discount)
   - **Dimensions**: `dim_customer`, `dim_product`, `dim_date`, `dim_store`
2. Write `create_warehouse.py`:
   - Creates the star schema in DuckDB
   - Generates and loads realistic sample data (10K orders, 500 customers, 200 products)
   - Implements SCD Type 2 for `dim_customer`: track address changes with `valid_from`, `valid_to`, `is_current`
3. Write dbt models (or SQL scripts if dbt setup is complex):
   - `staging/stg_orders.sql` — clean raw orders
   - `staging/stg_customers.sql` — clean raw customers
   - `marts/fct_orders.sql` — fact table with surrogate keys
   - `marts/dim_customer.sql` — SCD Type 2 dimension
   - `marts/monthly_revenue.sql` — aggregate mart
   - Add dbt tests: unique, not_null, accepted_values, relationships
4. Write `data_model_docs.md`:
   - Entity‑Relationship diagram (Mermaid)
   - Data dictionary: table, column, type, description, example
   - SCD Type 2 explanation with before/after example
   - Star schema vs normalised: when to use each

**Deliverables:**
1. `/data_engineer/task7/create_warehouse.py`
2. `/data_engineer/task7/models/` — SQL model files (staging + marts)
3. `/data_engineer/task7/data_model_docs.md` — ER diagram + data dictionary
4. `/data_engineer/task7/scd_demo.md` — SCD Type 2 walkthrough with examples
5. `/data_engineer/task7/requirements.txt`

---

## Task 8: Data Lake Architecture — Partitioning, Cataloguing & Lakehouse

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- Data lake organisation: bronze / silver / gold layers (medallion architecture)
- Partitioning strategies: by date, by category — for query performance
- Data cataloguing: metadata management
- Delta Lake / Iceberg format concepts (open table formats)
- Local lakehouse with DuckDB + Parquet

**What to read first:**
- 📖 [Databricks: Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture) (bronze/silver/gold)
- 📖 [Delta Lake Documentation](https://delta.io/) (open‑source table format)
- 📖 [Apache Iceberg: Overview](https://iceberg.apache.org/) (alternative table format)
- 📖 [DuckDB + Parquet: Local Lakehouse](https://duckdb.org/docs/data/parquet/overview.html)

**Task:**
1. Write `build_lakehouse.py` that creates a local data lake:
   - **Bronze layer** (`data/bronze/`): raw data as‑is, partitioned by `ingestion_date`
   - **Silver layer** (`data/silver/`): cleaned, deduplicated, typed, partitioned by `event_date`
   - **Gold layer** (`data/gold/`): business‑level aggregates (daily_revenue, customer_segments)
   - Use Parquet format with Hive‑style partitioning (`year=2024/month=01/day=15/`)
2. Write `partition_benchmark.py`:
   - Generate 1M rows of event data spanning 12 months
   - Save as: single file, partitioned by month, partitioned by day
   - Query: "revenue for March 2024" on each layout — compare query time
   - Show partition pruning in action (DuckDB scans only relevant partitions)
3. Write `data_catalog.py`:
   - Scan the data lake directory structure
   - For each table: record name, path, format, partitions, row count, columns, last modified
   - Save the catalog as `catalog.json`
   - Print a human‑readable summary table
4. Write `lakehouse_architecture.md`:
   - Diagram: bronze → silver → gold pipeline
   - Partitioning decision guide: when to partition, by what, too many partitions problem
   - Medallion architecture explained with your concrete examples
   - Open table formats (Delta vs Iceberg): what problem do they solve?

**Deliverables:**
1. `/data_engineer/task8/build_lakehouse.py`
2. `/data_engineer/task8/partition_benchmark.py`
3. `/data_engineer/task8/data_catalog.py`
4. `/data_engineer/task8/lakehouse_architecture.md`
5. `/data_engineer/task8/requirements.txt`

---

## Task 9: Infrastructure as Code — Docker, Docker Compose & CI/CD for Data Pipelines

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Containerising data pipeline components
- Docker Compose for multi‑service setups
- CI/CD for data pipelines: automated testing and deployment
- Environment management: dev vs staging vs prod
- Secrets management basics

**What to read first:**
- 📖 [Docker: Getting Started](https://docs.docker.com/get-started/) (official, first 5 parts)
- 📖 [Docker Compose Tutorial](https://docs.docker.com/compose/gettingstarted/) (multi‑service)
- 📖 [GitHub Actions for Data Pipelines](https://docs.github.com/en/actions/quickstart)
- 📖 [12‑Factor App: Config](https://12factor.net/config) (environment variables best practice)

**Task:**
1. Containerise your ETL pipeline (from Tasks 3–4):
   - Write `Dockerfile.etl` — Python container with pipeline code + dependencies
   - Write `Dockerfile.dashboard` — Streamlit dashboard (if you have one from Task 6)
2. Write `docker-compose.yml`:
   - Service 1: ETL pipeline (runs on schedule or on‑demand)
   - Service 2: DuckDB/data warehouse (persistent volume)
   - Service 3: Dashboard/API for querying results
   - Shared volumes for data exchange between services
   - Environment variables for configuration (no hardcoded paths/credentials)
3. Write `Makefile` with commands:
   - `make build` — build all images
   - `make run` — start all services
   - `make test` — run pipeline tests
   - `make lint` — run linters
   - `make clean` — stop and remove containers + volumes
4. Write `.github/workflows/data_pipeline.yml`:
   - On push: lint → test → build Docker image → run a smoke test (small data)
   - On schedule (weekly): run full pipeline integration test
5. Write `infrastructure_notes.md`:
   - Local dev setup instructions (step by step)
   - How to add a new data source (checklist)
   - Secrets management: env vars vs .env files vs vault (comparison)

**Deliverables:**
1. `/data_engineer/task9/Dockerfile.etl` + `Dockerfile.dashboard`
2. `/data_engineer/task9/docker-compose.yml`
3. `/data_engineer/task9/Makefile`
4. `/data_engineer/task9/.github/workflows/data_pipeline.yml`
5. `/data_engineer/task9/infrastructure_notes.md`

---

## Task 10: Monitoring, Alerting & Data Pipeline Observability

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Pipeline observability: logs, metrics, traces
- Data freshness monitoring: is the data up to date?
- Pipeline performance monitoring: latency, throughput, failure rates
- Alerting: when to alert vs when to log
- Runbooks: what to do when things break

**What to read first:**
- 📖 [Prometheus: Getting Started](https://prometheus.io/docs/prometheus/latest/getting_started/) (metrics collection)
- 📖 [Grafana: Getting Started](https://grafana.com/docs/grafana/latest/getting-started/) (dashboards)
- 📖 [Python logging Best Practices](https://docs.python.org/3/howto/logging.html) (structured logging)
- 📖 [Data Observability — Monte Carlo (Concepts)](https://www.montecarlodata.com/blog-data-observability/)

**Task:**
1. Write `pipeline_logger.py` — a structured logging module:
   - JSON‑formatted logs with: timestamp, level, pipeline_name, task_name, duration_ms, row_count, status
   - Log to both console and file (`logs/pipeline.log`)
   - Log rotation: new file per day, keep last 7 days
2. Write `pipeline_metrics.py`:
   - Track metrics for each pipeline run: start_time, end_time, duration, rows_processed, rows_failed, memory_used
   - Save metrics to `metrics/pipeline_metrics.csv` (append mode)
   - Compute: average run time, P95 run time, failure rate, data freshness (time since last successful run)
3. Write `monitoring_dashboard.py` using Streamlit:
   - Read the metrics CSV and show:
     - Pipeline health: last 10 runs (green/red), average duration trend
     - Data freshness: hours since last update per table (alert if > 24 hours)
     - Error log viewer: filter by date, level, pipeline
     - Performance chart: run duration over time with P95 line
4. Write `alerting.py`:
   - Define alert rules: pipeline failed, data stale > 24h, run time > 2x average, error rate > 10%
   - When triggered: log the alert, write to `alerts/alerts.jsonl`
   - (Optional) Send a desktop notification or write to a Slack‑compatible webhook format
5. Write `runbook.md`:
   - For each alert type: what it means, likely root causes, diagnostic steps, fix steps
   - Escalation policy: when to fix yourself vs when to escalate
   - Post‑mortem template: what happened, impact, root cause, fix, prevention

**Deliverables:**
1. `/data_engineer/task10/pipeline_logger.py`
2. `/data_engineer/task10/pipeline_metrics.py`
3. `/data_engineer/task10/monitoring_dashboard.py`
4. `/data_engineer/task10/alerting.py`
5. `/data_engineer/task10/runbook.md` — incident response + post‑mortem template

---

## Learning Path Summary

| Task | Topic | Difficulty | Key Tools |
|------|-------|-----------|-----------|
| 1 | Data Formats & Serialisation | ⭐ | Parquet, DuckDB, Avro |
| 2 | Advanced SQL | ⭐⭐ | DuckDB/SQLite, SQL |
| 3 | ETL Pipeline | ⭐⭐ | Python, DuckDB, APIs |
| 4 | Workflow Orchestration | ⭐⭐⭐ | Airflow/Prefect |
| 5 | Data Quality & Testing | ⭐⭐⭐ | Great Expectations |
| 6 | Stream Processing | ⭐⭐⭐ | Python, Redis/File Streams |
| 7 | Data Modelling (Star Schema + dbt) | ⭐⭐⭐⭐ | dbt, DuckDB |
| 8 | Data Lake Architecture | ⭐⭐⭐⭐ | Parquet, DuckDB, Delta Lake |
| 9 | Infrastructure as Code (Docker + CI/CD) | ⭐⭐⭐⭐⭐ | Docker, GitHub Actions |
| 10 | Pipeline Monitoring & Observability | ⭐⭐⭐⭐⭐ | Streamlit, Prometheus concepts |

**All tools are free and open‑source. No paid cloud services required.**
