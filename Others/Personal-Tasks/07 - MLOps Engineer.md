# MLOps Engineer — 10 Tasks (Beginner → 2‑Year Experience)

> **Goal:** Go from "I know Python and basic ML" to "I can deploy, monitor, and maintain ML systems in production reliably."
> An MLOps Engineer bridges the gap between data science experiments and production systems — you make ML models reliable, reproducible, and scalable.
> Each task is self‑contained. Difficulty increases from Task 1 → 10.

---

## Task 1: Version Control for ML — Git, DVC & Experiment Reproducibility

**Difficulty:** ⭐ Beginner

**What you'll learn:**
- Git best practices for ML projects (what to commit, what to ignore)
- Data versioning with DVC (Data Version Control)
- Reproducible experiments: pinning dependencies, random seeds, config files
- Project structure for ML repos

**What to read first:**
- 📖 [DVC: Getting Started](https://dvc.org/doc/start) (30 min)
- 📖 [Cookiecutter Data Science: Project Structure](https://drivendata.github.io/cookiecutter-data-science/) (best practices)
- 📖 [Git for Data Science — Real Python](https://realpython.com/python-git-github-intro/) (refresher)
- 📖 [Made With ML: Versioning](https://madewithml.com/courses/mlops/versioning/) (free)

**Task:**
1. Create a well‑structured ML project repo:
   ```
   ml_project/
   ├── .gitignore          # ignore data/, models/, *.pkl, __pycache__
   ├── .dvc/               # DVC config
   ├── data/raw/           # DVC‑tracked
   ├── data/processed/     # DVC‑tracked
   ├── models/             # DVC‑tracked
   ├── src/train.py, predict.py, evaluate.py
   ├── configs/config.yaml
   ├── requirements.txt    # pinned versions
   └── README.md
   ```
2. Write `setup_dvc.sh`:
   - Initialise DVC in the repo
   - Add a dataset (any CSV ~10K rows) to DVC tracking
   - Configure a local remote (`/tmp/dvc_remote` or a folder in the project)
   - Push the data to the remote
   - Show: changing the data, committing the new version, switching between versions
3. Write `reproducible_train.py`:
   - Reads all hyperparameters from `configs/config.yaml` (not hardcoded)
   - Sets random seed (Python, NumPy, sklearn)
   - Trains a model, saves it with DVC
   - Logs: config hash, data hash (MD5 of the CSV), model hash, metrics
   - Running the same script twice produces the **exact same** model and metrics
4. Write `reproducibility_checklist.md`:
   - 10‑item checklist: seed, config, data version, dependency pinning, etc.
   - Common pitfalls: floating‑point non‑determinism, data leakage in preprocessing

**Deliverables:**
1. `/mlops_engineer/task1/setup_dvc.sh`
2. `/mlops_engineer/task1/reproducible_train.py`
3. `/mlops_engineer/task1/configs/config.yaml`
4. `/mlops_engineer/task1/reproducibility_checklist.md`
5. `/mlops_engineer/task1/requirements.txt`

---

## Task 2: ML Pipeline Automation — From Script to Pipeline

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- Converting Jupyter notebooks and scripts into reproducible pipelines
- DVC pipelines (dvc.yaml): defining stages and dependencies
- Makefile‑based automation
- The concept of DAGs (Directed Acyclic Graphs) in ML workflows

**What to read first:**
- 📖 [DVC: Pipelines](https://dvc.org/doc/user-guide/pipelines) (official guide)
- 📖 [Makefiles for Data Science](https://the-turing-way.netlify.app/reproducible-research/make.html) (The Turing Way)
- 📖 [Kedro: ML Pipeline Framework](https://docs.kedro.org/en/stable/get_started/index.html) (alternative)

**Task:**
1. Take a typical ML workflow (preprocess → feature engineer → train → evaluate) and convert it to a DVC pipeline.
2. Write `dvc.yaml` defining 4 stages:
   ```yaml
   stages:
     preprocess:
       cmd: python src/preprocess.py
       deps: [data/raw/dataset.csv, src/preprocess.py]
       outs: [data/processed/train.csv, data/processed/test.csv]
     train:
       cmd: python src/train.py
       deps: [data/processed/train.csv, src/train.py, configs/config.yaml]
       outs: [models/model.pkl]
       params: [configs/config.yaml]
     evaluate:
       cmd: python src/evaluate.py
       deps: [models/model.pkl, data/processed/test.csv, src/evaluate.py]
       metrics: [reports/metrics.json]
       plots: [reports/confusion_matrix.csv]
   ```
3. Write each stage script: `src/preprocess.py`, `src/train.py`, `src/evaluate.py`.
4. Write a `Makefile` with targets:
   - `make pipeline` — runs `dvc repro` (only re‑runs changed stages)
   - `make train` — force re‑train
   - `make evaluate` — just evaluate
   - `make clean` — remove all generated artifacts
   - `make lint` — run flake8 + black
5. Demonstrate caching: change only the config → show that only train + evaluate re‑run (preprocess is cached).

**Deliverables:**
1. `/mlops_engineer/task2/dvc.yaml`
2. `/mlops_engineer/task2/src/preprocess.py`, `train.py`, `evaluate.py`
3. `/mlops_engineer/task2/Makefile`
4. `/mlops_engineer/task2/pipeline_notes.md` — caching demo + DVC vs Airflow comparison
5. `/mlops_engineer/task2/requirements.txt`

---

## Task 3: Model Registry & Lifecycle Management with MLflow

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- MLflow Tracking: logging experiments, parameters, metrics, artifacts
- MLflow Model Registry: versioning models with stage transitions
- Model lifecycle: None → Staging → Production → Archived
- Loading models from the registry for serving

**What to read first:**
- 📖 [MLflow: Model Registry](https://mlflow.org/docs/latest/model-registry.html) (official guide)
- 📖 [MLflow: Quickstart](https://mlflow.org/docs/latest/getting-started/index.html) (30 min)
- 📖 [Neptune.ai: Experiment Tracking Comparison](https://neptune.ai/blog/best-ml-experiment-tracking-tools) (landscape overview)

**Task:**
1. Write `train_and_log.py`:
   - Creates an MLflow experiment
   - Trains 3 model variants (different algorithms or hyperparams)
   - For each run, logs: all hyperparameters, metrics (accuracy, F1, AUC, latency), model artifact, training data hash, feature names, a confusion matrix plot
   - Tags: `model_type`, `dataset`, `author`, `commit_hash`
2. Write `register_best_model.py`:
   - Finds the best run by a specified metric (e.g., F1)
   - Registers it in the MLflow Model Registry under a model name
   - Adds a description and tags
   - Transitions to "Staging"
3. Write `promote_model.py`:
   - Loads the Staging model
   - Runs validation checks: accuracy > threshold, latency < threshold, no NaN predictions
   - If all pass → transition to "Production"
   - If any fail → log the failure reason and keep in Staging
4. Write `load_production_model.py`:
   - Loads the current Production model from the registry
   - Makes predictions on sample data
   - Prints model metadata (version, creation date, metrics)
5. Write `model_lifecycle.md`:
   - Diagram: None → Staging → Production → Archived
   - What checks should gate each transition?
   - Rollback strategy: what if the new model is worse in production?

**Deliverables:**
1. `/mlops_engineer/task3/train_and_log.py`
2. `/mlops_engineer/task3/register_best_model.py`
3. `/mlops_engineer/task3/promote_model.py`
4. `/mlops_engineer/task3/load_production_model.py`
5. `/mlops_engineer/task3/model_lifecycle.md` — lifecycle diagram + promotion criteria

---

## Task 4: Model Serving — FastAPI, Docker & Load Testing

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Building a production‑grade prediction API (FastAPI)
- Request validation, error handling, and logging
- Containerising with Docker (multi‑stage builds)
- Load testing: understanding throughput and latency under load
- Graceful degradation and health checks

**What to read first:**
- 📖 [FastAPI: Production Best Practices](https://fastapi.tiangolo.com/deployment/) (official)
- 📖 [Docker: Multi‑Stage Builds](https://docs.docker.com/build/building/multi-stage/) (smaller images)
- 📖 [Locust: Load Testing](https://docs.locust.io/en/stable/quickstart.html) (Python load testing)
- 📖 [Uvicorn: Deployment](https://www.uvicorn.org/deployment/) (ASGI server)

**Task:**
1. Write `app.py` (FastAPI) with:
   - `POST /predict` — accepts features as JSON, returns prediction + probability + model version
   - `POST /predict/batch` — accepts a list of inputs, returns batch predictions
   - `GET /health` — returns status, model version, uptime, last prediction time
   - `GET /model-info` — returns feature names, model type, training metrics
   - Structured logging: log every request (input hash, latency, status code)
   - Error handling: return meaningful errors for bad input, model failures
2. Write `Dockerfile`:
   - Multi‑stage build: deps stage → app stage
   - Non‑root user
   - Health check instruction
   - Minimal image size (use slim base)
3. Write `docker-compose.yml`:
   - API service (2 replicas behind a reverse proxy — or just 2 instances on different ports)
   - Volume mount for model file
   - Environment variables for config
4. Write `load_test.py` using Locust:
   - Simulate 50 concurrent users sending requests for 2 minutes
   - Mix: 80% single predictions, 20% batch predictions
   - Report: median latency, P95 latency, P99 latency, requests/second, error rate
5. Write `serving_report.md`:
   - Load test results table + charts
   - Where is the bottleneck? (model inference, serialization, network?)
   - Scaling strategy: when to add replicas vs optimise model

**Deliverables:**
1. `/mlops_engineer/task4/app.py`
2. `/mlops_engineer/task4/Dockerfile` + `docker-compose.yml`
3. `/mlops_engineer/task4/load_test.py` — Locust load test
4. `/mlops_engineer/task4/serving_report.md` — load test results + analysis
5. `/mlops_engineer/task4/requirements.txt`

---

## Task 5: Model Monitoring — Drift Detection & Performance Tracking

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Data drift vs concept drift vs prediction drift
- Statistical tests for drift: KS test, PSI, chi‑squared
- Monitoring model performance in production (when you have delayed labels)
- Setting up alerts for model degradation

**What to read first:**
- 📖 [Evidently AI: ML Monitoring Guide](https://docs.evidentlyai.com/) (open‑source, excellent)
- 📖 [NannyML: Estimating Performance Without Labels](https://nannyml.readthedocs.io/en/stable/) (innovative approach)
- 📖 [Google: ML Technical Debt](https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html) (classic paper)
- 📖 [Alibi Detect: Drift Detection](https://docs.seldon.io/projects/alibi-detect/en/stable/) (open‑source)

**Task:**
1. Write `simulate_production.py`:
   - Train a model on "historical" data (January–June)
   - Generate 6 months of "production" data (July–December) with:
     - Months 7–9: same distribution (no drift)
     - Month 10: gradual feature drift (shift mean of 2 features by 0.5 std)
     - Month 11: sudden feature drift (shift mean by 2 std)
     - Month 12: concept drift (change the relationship between features and target)
2. Write `drift_detector.py`:
   - For each month's production data, compare to training data:
     - Per‑feature KS test (p‑value < 0.05 = drift detected)
     - Population Stability Index (PSI) per feature (PSI > 0.2 = significant drift)
     - Prediction distribution shift (compare predicted probability distributions)
   - Output a monthly drift report: feature, test, statistic, p_value, drift_detected
3. Write `performance_monitor.py`:
   - Simulate delayed labels arriving (labels come 2 weeks after prediction)
   - Track weekly: accuracy, F1, precision, recall
   - Plot performance over time — show degradation correlating with drift
   - Set thresholds: alert if F1 drops below 0.7 or PSI > 0.25
4. Write `monitoring_dashboard.py` (Streamlit):
   - Feature drift heatmap: month × feature, coloured by PSI
   - Performance timeline: metrics over time with alert thresholds
   - Drill‑down: click a drifted feature → see distribution comparison (training vs production)
5. Write `monitoring_playbook.md`:
   - What to do when drift is detected (retrain? roll back? alert?)
   - Decision tree: data drift detected → is performance degraded? → yes → retrain on recent data
   - How often to check for drift
   - False alarm reduction strategies

**Deliverables:**
1. `/mlops_engineer/task5/simulate_production.py`
2. `/mlops_engineer/task5/drift_detector.py`
3. `/mlops_engineer/task5/performance_monitor.py`
4. `/mlops_engineer/task5/monitoring_dashboard.py`
5. `/mlops_engineer/task5/monitoring_playbook.md`

---

## Task 6: CI/CD for ML — Automated Training, Testing & Deployment

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- CI/CD pipelines for ML: different from traditional software CI/CD
- Automated model testing: unit tests, data tests, model quality tests
- Validation gates: new model must beat the champion
- GitHub Actions for ML workflows
- Blue/green deployment concepts

**What to read first:**
- 📖 [Made With ML: CI/CD for ML](https://madewithml.com/courses/mlops/cicd/) (free)
- 📖 [Martin Fowler: CD4ML](https://martinfowler.com/articles/cd4ml.html) (comprehensive)
- 📖 [GitHub Actions: Quickstart](https://docs.github.com/en/actions/quickstart)
- 📖 [CML: Continuous Machine Learning](https://cml.dev/doc/start) (by DVC team)

**Task:**
1. Write a comprehensive test suite:
   - `tests/test_data.py`: schema validation, no nulls in critical columns, correct split ratio, data shape bounds
   - `tests/test_features.py`: feature ranges, no leakage (target not in features), encoding correctness
   - `tests/test_model.py`: model loads, output shape correct, predictions in valid range, latency < 100ms, no NaN predictions
   - `tests/test_api.py`: API returns 200 for valid input, 422 for invalid, correct response schema
2. Write `validate_model.py`:
   - Load the new candidate model and the current champion model
   - Run both on the same holdout test set
   - Compare: the candidate must beat the champion on F1 by at least 0.01 (configurable threshold)
   - Check model size (< 500MB), inference latency (< 100ms per prediction)
   - Output: PASS/FAIL with detailed comparison
3. Write `.github/workflows/ml_ci.yml`:
   - **On pull request**: lint (flake8/ruff) → unit tests → data tests → train on small sample → model tests → comment results on PR
   - **On merge to main**: full training → validate vs champion → if pass → register model → deploy API
4. Write `deployment_strategy.md`:
   - Blue/green deployment explained with diagram
   - Canary deployment: route 10% of traffic to new model, monitor, then roll out
   - Rollback procedure: step‑by‑step
   - Feature flags for model versions

**Deliverables:**
1. `/mlops_engineer/task6/tests/` — test_data.py, test_features.py, test_model.py, test_api.py
2. `/mlops_engineer/task6/validate_model.py`
3. `/mlops_engineer/task6/.github/workflows/ml_ci.yml`
4. `/mlops_engineer/task6/deployment_strategy.md`
5. `/mlops_engineer/task6/requirements.txt`

---

## Task 7: Feature Store — Compute, Store & Serve Features

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- What a feature store is and why it matters
- Online vs offline feature serving
- Feature computation pipelines: batch and real‑time
- Feature reuse across models and teams
- Point‑in‑time correctness (avoiding data leakage)

**What to read first:**
- 📖 [Feast: Getting Started](https://docs.feast.dev/getting-started/quickstart) (open‑source feature store)
- 📖 [Tecton: What is a Feature Store?](https://www.tecton.ai/blog/what-is-a-feature-store/) (concepts)
- 📖 [Uber: Michelangelo Feature Store](https://www.uber.com/en-IN/blog/michelangelo-machine-learning-platform/) (architecture inspiration)

**Task:**
1. Write `feature_definitions.py`:
   - Define 15+ features for an e‑commerce use case:
     - **User features**: total_orders_30d, avg_order_value_30d, days_since_last_order, favourite_category
     - **Product features**: avg_rating, total_reviews, price_percentile, return_rate
     - **Interaction features**: user_viewed_product_count, user_cart_abandonment_rate
   - Each feature: name, type, description, computation logic, freshness requirement
2. Write `feature_pipeline.py`:
   - Compute batch features from historical data (SQL or Pandas)
   - Implement point‑in‑time joins: for a given prediction date, only use data available before that date (no leakage)
   - Save features to a feature store (Feast on local file store, or a simple Parquet‑based store)
   - Log: computation time, row count, null rate per feature
3. Write `feature_server.py`:
   - A FastAPI endpoint that serves features:
     - `GET /features/{user_id}` → returns the latest feature values for a user
     - `POST /features/batch` → returns features for a list of user_ids
   - Simulates online serving with caching (use a dict or Redis)
4. Write `feature_store_report.md`:
   - Architecture diagram: data sources → feature pipeline → store → online/offline serving
   - Point‑in‑time correctness explained with a concrete example
   - Feature documentation template
   - When you need a feature store vs when a simple SQL view is enough

**Deliverables:**
1. `/mlops_engineer/task7/feature_definitions.py`
2. `/mlops_engineer/task7/feature_pipeline.py`
3. `/mlops_engineer/task7/feature_server.py`
4. `/mlops_engineer/task7/feature_store_report.md`
5. `/mlops_engineer/task7/requirements.txt`

---

## Task 8: Model Optimisation for Production — Quantisation, ONNX & Latency Reduction

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- Model compression: pruning, quantisation, distillation concepts
- ONNX: cross‑framework model format
- ONNX Runtime: optimised inference
- Latency profiling and optimisation
- Model size vs accuracy trade‑offs

**What to read first:**
- 📖 [ONNX: Getting Started](https://onnx.ai/get-started.html)
- 📖 [ONNX Runtime: Performance Tuning](https://onnxruntime.ai/docs/performance/tune-performance/overview.html)
- 📖 [Hugging Face: Optimum (ONNX export)](https://huggingface.co/docs/optimum/onnxruntime/overview)
- 📖 [PyTorch: Quantization](https://pytorch.org/docs/stable/quantization.html) (docs)

**Task:**
1. Train a model that's large enough to optimise (e.g., a fine‑tuned DistilBERT for text classification, or a ResNet for image classification).
2. Write `export_onnx.py`:
   - Export the trained model to ONNX format
   - Validate: run the same inputs through the original and ONNX model → outputs should match (within tolerance)
   - Compare model file sizes: original vs ONNX
3. Write `quantise_model.py`:
   - Apply dynamic quantisation (INT8) to the ONNX model
   - Apply static quantisation (if applicable) — requires calibration data
   - Compare: original FP32 vs dynamic INT8 vs static INT8 on accuracy and file size
4. Write `benchmark_inference.py`:
   - Benchmark all model variants on the same 1,000 inputs:
     - Original (PyTorch/sklearn)
     - ONNX (FP32)
     - ONNX (INT8 quantised)
   - Measure: mean latency, P50, P95, P99 latency, throughput (predictions/sec), memory usage
   - Run with batch sizes: 1, 8, 32, 64 → show how batching affects throughput
5. Write `optimisation_report.md`:
   - Table: model variant, file size, accuracy, P95 latency, throughput
   - Did quantisation hurt accuracy? By how much?
   - Decision guide: when to quantise, when to use ONNX, when to keep the original
   - Cost analysis: "Reducing latency by 3x means we need 3x fewer servers"

**Deliverables:**
1. `/mlops_engineer/task8/export_onnx.py`
2. `/mlops_engineer/task8/quantise_model.py`
3. `/mlops_engineer/task8/benchmark_inference.py`
4. `/mlops_engineer/task8/optimisation_report.md`
5. `/mlops_engineer/task8/requirements.txt`

---

## Task 9: Infrastructure as Code — Kubernetes Concepts & Helm Charts for ML

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Kubernetes concepts: pods, deployments, services, ingress
- Deploying ML services on Kubernetes (locally with Kind or Minikube)
- Helm charts for templated deployments
- Horizontal Pod Autoscaling (HPA) for ML workloads
- Resource management: CPU/memory requests and limits

**What to read first:**
- 📖 [Kubernetes: Learn Kubernetes Basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/) (official, interactive)
- 📖 [Kind: Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/) (local Kubernetes cluster)
- 📖 [Helm: Getting Started](https://helm.sh/docs/intro/quickstart/) (package manager for K8s)
- 📖 [KServe: Serving ML Models on K8s](https://kserve.github.io/website/latest/) (ML‑specific serving)

**Task:**
1. Write Kubernetes manifests for your ML API:
   - `deployment.yaml`: 2 replicas, resource limits (CPU: 500m, Memory: 512Mi), readiness + liveness probes
   - `service.yaml`: ClusterIP service exposing the API
   - `ingress.yaml`: route `/predict` to the service
   - `configmap.yaml`: model version, feature config
   - `hpa.yaml`: auto‑scale from 2 to 10 replicas based on CPU utilisation > 70%
2. Write a Helm chart (`helm/ml-api/`):
   - Templatise the manifests: image tag, replicas, resources, model version as values
   - `values.yaml` for dev, `values-prod.yaml` for production (different resources, replicas)
   - Demonstrate: `helm install` with dev values, then upgrade with prod values
3. Test locally with Kind or Minikube:
   - Create a local cluster
   - Deploy your API
   - Verify health endpoint works
   - Show HPA in action: generate load → watch replicas scale up
4. Write `k8s_architecture.md`:
   - Diagram: client → ingress → service → pods (replicas) → model storage
   - When to use Kubernetes for ML vs simpler alternatives (Docker Compose, serverless)
   - Resource planning: how to estimate CPU/memory for ML workloads
   - Common pitfalls: OOMKills, cold starts, GPU scheduling

**Deliverables:**
1. `/mlops_engineer/task9/k8s/` — deployment.yaml, service.yaml, ingress.yaml, configmap.yaml, hpa.yaml
2. `/mlops_engineer/task9/helm/ml-api/` — Chart.yaml, values.yaml, templates/
3. `/mlops_engineer/task9/k8s_architecture.md`
4. `/mlops_engineer/task9/setup_local_cluster.sh` — script to create Kind cluster + deploy
5. `/mlops_engineer/task9/requirements.txt`

---

## Task 10: End‑to‑End MLOps Platform — Tying It All Together

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Designing a complete MLOps platform architecture
- Integrating all components: version control, pipelines, registry, serving, monitoring
- Automated retraining triggers
- Incident response for ML systems
- Platform documentation and onboarding

**What to read first:**
- 📖 [Google: MLOps Maturity Model](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning) (levels 0–2)
- 📖 [Chip Huyen: Designing Machine Learning Systems](https://huyenchip.com/machine-learning-systems-design/toc.html) (book outline, free)
- 📖 [MLOps Community](https://mlops.community/) — case studies and discussions
- 📖 [Evidently + MLflow + Airflow Integration](https://docs.evidentlyai.com/) (end‑to‑end example)

**Task:**
1. Write `platform_architecture.md`:
   - Design the complete MLOps platform using tools from Tasks 1–9:
     - **Version Control**: Git + DVC
     - **Pipeline**: DVC pipelines + Airflow for scheduling
     - **Experiment Tracking**: MLflow
     - **Model Registry**: MLflow Model Registry
     - **Serving**: FastAPI + Docker + Kubernetes
     - **Monitoring**: Evidently + custom dashboards
     - **CI/CD**: GitHub Actions
     - **Feature Store**: Feast (or custom)
   - Architecture diagram (Mermaid): how all components connect
   - Data flow diagram: from raw data to prediction
   - MLOps maturity levels: where does your platform sit?
2. Write `auto_retrain.py`:
   - A script that checks for model drift (from Task 5)
   - If drift detected → triggers the training pipeline (from Task 2)
   - Validates the new model against the champion (from Task 6)
   - If better → promotes to production
   - If worse → logs and alerts
   - The full loop: detect → retrain → validate → deploy (or reject)
3. Write `platform_runbook.md`:
   - **Onboarding**: step‑by‑step for a new team member to set up the platform locally
   - **Adding a new model**: checklist (data, features, training, serving, monitoring)
   - **Incident response**: what to do when the model serves bad predictions
   - **Operational playbook**: daily/weekly/monthly tasks for the MLOps engineer
4. Write `mlops_maturity_assessment.md`:
   - Evaluate your platform against Google's MLOps maturity levels (0, 1, 2)
   - What you built: Level 1 capabilities
   - What's needed for Level 2: automated retraining, automated testing, feature stores, A/B testing in production
   - Roadmap: 3 things to build next

**Deliverables:**
1. `/mlops_engineer/task10/platform_architecture.md` — full architecture + diagrams
2. `/mlops_engineer/task10/auto_retrain.py`
3. `/mlops_engineer/task10/platform_runbook.md` — onboarding + incident response
4. `/mlops_engineer/task10/mlops_maturity_assessment.md`
5. `/mlops_engineer/task10/component_integration_test.py` — smoke test that verifies all components work together

---

## Learning Path Summary

| Task | Topic | Difficulty | Key Tools |
|------|-------|-----------|-----------|
| 1 | Version Control (Git + DVC) | ⭐ | Git, DVC |
| 2 | ML Pipeline Automation | ⭐⭐ | DVC Pipelines, Make |
| 3 | Model Registry & Lifecycle (MLflow) | ⭐⭐ | MLflow |
| 4 | Model Serving (FastAPI + Docker) | ⭐⭐⭐ | FastAPI, Docker, Locust |
| 5 | Model Monitoring & Drift Detection | ⭐⭐⭐ | Evidently, Scikit‑learn |
| 6 | CI/CD for ML | ⭐⭐⭐⭐ | GitHub Actions, pytest |
| 7 | Feature Store | ⭐⭐⭐⭐ | Feast, FastAPI |
| 8 | Model Optimisation (ONNX + Quantisation) | ⭐⭐⭐⭐ | ONNX Runtime, PyTorch |
| 9 | Kubernetes for ML | ⭐⭐⭐⭐⭐ | Kind/Minikube, Helm, K8s |
| 10 | End‑to‑End MLOps Platform | ⭐⭐⭐⭐⭐ | All of the above |

**All tools are free and open‑source. No paid cloud services required.**
