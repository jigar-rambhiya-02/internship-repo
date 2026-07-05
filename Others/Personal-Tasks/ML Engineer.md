# Machine Learning Engineer Bootcamp – 5 Real‑World Tasks

## Task 1: Train a Production‑Ready Model with Proper Validation & Versioning

**Goal:** Move beyond notebook‑only training – build a reproducible training pipeline that logs metrics, saves model artifacts, and tracks hyperparameters.

**Concepts:**
- Train/validation/test split with stratification
- Cross‑validation for hyperparameter tuning
- Model versioning (MLflow / DVC / Weights & Biases)
- Metrics selection (business vs technical)

**Steps:**
1. Pick a public dataset (e.g., tabular – Kaggle’s “Home Credit Default Risk”, or image – CIFAR‑10, or text – IMDB reviews).
2. Write `train.py` that:
   - Loads data, performs a clean train/val/test split (60/20/20) with stratification.
   - Trains 3 baseline models (e.g., LogisticRegression, RandomForest, XGBoost for tabular).
   - Tunes hyperparameters using 5‑fold CV on training set.
   - Logs all hyperparameters, metrics (accuracy, precision, recall, F1, ROC‑AUC) to MLflow.
   - Saves the best model as `model.pkl` (or `.joblib`) along with a metadata file (`model_metadata.json`).
3. Compute test‑set performance and log as a separate run.
4. Write a short `README.md` explaining how to reproduce the training from scratch.

**Deliverables:**
1. `/ml_engineer/task1/train.py`
2. `/ml_engineer/task1/requirements.txt`
3. `/ml_engineer/task1/model_metadata.json` – contains: best_params, test_metrics, training_timestamp, data_hash
4. `/ml_engineer/task1/mlflow_run_id.txt` – ID of the best run
5. `/ml_engineer/task1/reproducibility_notes.md` – how to rerun and get same results (seeds, env)

---

## Task 2: Deploy a Model as a REST API with Latency & Load Testing

**Goal:** Package a trained model into a production API, add basic monitoring, and verify it can handle realistic traffic.

**Concepts:**
- Model serialisation (ONNX, Pickle, TensorFlow SavedModel)
- API frameworks (FastAPI, Flask) with async support
- Request/response schemas (Pydantic)
- Load testing (locust / k6)
- Basic health checks and metrics endpoint

**Steps:**
1. Use the best model from Task 1 (or a pre‑trained small model like a scikit‑learn pipeline).
2. Build `app.py` with FastAPI that includes:
   - `POST /predict` endpoint – accepts JSON input, returns prediction + confidence
   - `GET /health` – returns 200 if model loaded
   - `GET /metrics` – exposes Prometheus‑style stats (request count, latency histogram)
3. Containerise with Docker (multi‑stage build for small image).
4. Run load test using Locust: simulate 50 concurrent users for 2 minutes. Measure p95 latency and error rate.
5. Optimise: add batching or async, compare performance before/after.
6. Write a `deployment.md` describing the API spec, resource limits (CPU/RAM), and expected QPS.

**Deliverables:**
1. `/ml_engineer/task2/app.py` + `Dockerfile`
2. `/ml_engineer/task2/locustfile.py` – load test script
3. `/ml_engineer/task2/load_test_results.csv` – percentiles, requests/sec, failures
4. `/ml_engineer/task2/deployment.md` – resource recommendations + API examples (curl)
5. `/ml_engineer/task2/optimisation_log.md` – what you changed and the improvement

---

## Task 3: Batch Inference Pipeline with Feature Store & Data Validation

**Goal:** Build a daily batch inference system that reads fresh data, validates it, fetches features, runs predictions, and writes back results – mimicking a real ML pipeline.

**Concepts:**
- Feature store pattern (Feast or simple SQLite / BigQuery)
- Data validation (Great Expectations / Pydantic)
- Idempotent batch processing
- Monitoring for data drift

**Steps:**
1. Create a simulated source: a CSV that grows daily (e.g., customer transactions). Use `faker` to generate 100 new rows per day.
2. Build a lightweight feature store:
   - `features/` folder with historical features computed from raw data
   - A registry YAML that maps features to sources
3. Write `batch_predict.py` that:
   - Reads new data from `data/new_<date>.csv`
   - Validates schema (column names, types, ranges) – fails loudly if invalid
   - Fetches required features (if missing, computes on the fly)
   - Loads the model from Task 2 (or a local copy) and generates predictions
   - Appends predictions to `predictions/preds_<date>.parquet`
4. Add a data drift check: compare feature distributions of new data vs training data (KS test / population stability index). If drift detected, send an alert (print to console).
5. Schedule the script to run daily (using cron or GitHub Actions) and keep 7 days of logs.

**Deliverables:**
1. `/ml_engineer/task3/batch_predict.py`
2. `/ml_engineer/task3/feature_store.yaml` – config for features
3. `/ml_engineer/task3/data_validation.py` – Great Expectations suite or custom validator
4. `/ml_engineer/task3/drift_report.html` – example drift report from one run
5. `/ml_engineer/task3/schedule_cron.txt` – the cron expression and command

---

## Task 4: Model Monitoring & Automated Retraining Trigger

**Goal:** Set up a monitoring dashboard that tracks model performance in production (or simulated) and triggers retraining when quality degrades.

**Concepts:**
- Performance monitoring (accuracy, F1, business KPI) when ground truth is delayed
- Concept drift detection (Kolmogorov‑Smirnov, Population Stability Index)
- Automated retraining pipeline (GitHub Actions / Airflow)
- Model registry (MLflow Model Registry) to promote stages

**Steps:**
1. Simulate a production environment: a script `simulate_production.py` that:
   - Every hour, generates 50 new inference requests (with known ground truth hidden)
   - Stores predictions in a table `predictions_log`
   - After a 6‑hour delay, backfills the true labels (simulate delayed feedback)
2. Write `monitor.py` that:
   - Queries predictions from last 24h where ground truth is available
   - Computes current performance (accuracy / F1) and compares to baseline
   - If performance drops below threshold (e.g., 5% absolute), logs a warning and creates a retraining trigger file (`/tmp/retrain_needed.txt`)
3. Write `retrain_trigger.py` – a separate script that, if the trigger file exists, starts a new training run (calls `train.py` from Task 1 with fresh data), registers the new model in MLflow, and transitions it to “Staging”.
4. Build a simple dashboard using Gradio or Streamlit that shows:
   - Performance over time (line chart)
   - Feature drift alerts
   - Last retraining timestamp and new model version

**Deliverables:**
1. `/ml_engineer/task4/simulate_production.py`
2. `/ml_engineer/task4/monitor.py` – drift & performance metrics
3. `/ml_engineer/task4/retrain_trigger.py`
4. `/ml_engineer/task4/dashboard.py` – Gradio or Streamlit app
5. `/ml_engineer/task4/monitoring_alerts.log` – example alerts from 3 days of simulation

---

## Task 5: End‑to‑End ML Pipeline with CI/CD (GitHub Actions + Model Validation Gates)

**Goal:** Create a full CI/CD pipeline for ML: on every code push, run tests, train a candidate model, validate it against the current production model, and (optionally) auto‑deploy if it passes.

**Concepts:**
- CI for ML: linting, unit tests, data validation
- Model validation gates: performance against baseline, inference latency, fairness checks
- Continuous Delivery: promote model to staging → production
- Infrastructure as code (Terraform / Cloud Run config)

**Steps:**
1. Structure your repo as:
```
/your_repo_root/
├── .github/
│   └── workflows/
│       └── ml_pipeline.yml
├── src/
│   ├── train.py
│   ├── predict.py
│   └── evaluate.py
├── tests/
│   ├── test_data.py
│   └── test_model.py
├── config/
│   └── thresholds.yaml
└── (optional other files like requirements.txt, Dockerfile, etc.)
```
2. Create a GitHub Actions workflow that triggers on push to `main` (or on demand):
- Step 1: Install dependencies, run linter (flake8/black) and pytest (unit + data tests).
- Step 2: Run training on a small sample (fast) to catch syntax errors.
- Step 3: If that passes, run full training on the complete dataset.
- Step 4: Evaluate candidate model against the currently deployed model (stored in MLflow). Compare metrics (e.g., candidate F1 must be >= current F1 – 0.02).
- Step 5: If it passes, automatically deploy to a staging endpoint (Cloud Run).
- Step 6: Run a smoke test (10 prediction requests) against staging.
- Step 7: (Optional) manual approval step before promoting to production.
1. Write a `thresholds.yaml` that defines:
- Minimum acceptable F1 (absolute)
- Maximum inference latency (ms)
- Allowed degradation vs current model
1. Deploy a production endpoint once (manually) and let CI/CD update it.

**Deliverables:**
1. `/ml_engineer/task5/.github/workflows/ml_pipeline.yml`
2. `/ml_engineer/task5/config/thresholds.yaml`
3. `/ml_engineer/task5/tests/test_model.py` – example unit tests (e.g., model output shape)
4. `/ml_engineer/task5/validation_report.md` – showing a run where candidate model passed gates, and one where it failed
5. `/ml_engineer/task5/production_endpoint.txt` – live URL after CI/CD deployment

---

## How to use this bootcamp

- Each task builds on the previous one (Task 1’s model → Task 2’s API → Task 3’s batch → Task 4’s monitoring → Task 5’s CI/CD).
- For a junior MLE, each task takes 1–2 days. Focus on **reproducibility** and **automation**.
- Use open‑source tools (MLflow, FastAPI, Great Expectations, GitHub Actions) – no paid tier needed.
- After finishing, you will have an end‑to‑end MLOps portfolio covering:
- Reproducible training + versioning
- Model serving (REST API + batch)
- Data validation + feature store
- Monitoring (drift + performance)
- CI/CD for ML with validation gates

**Recommended order:** 1 → 2 → 3 → 4 → 5 (sequential dependency is intentional).