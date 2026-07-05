# Machine Learning Engineer — 10 Tasks (Beginner → 2‑Year Experience)

> **Goal:** Go from "I know Python" to "I can build, serve, and monitor ML models in production."
> Each task is self‑contained — you can do them in any order, but difficulty increases from Task 1 → 10.
> Every task lists **what to read first** so you learn the theory before building.

---

## Task 1: Understand the ML Landscape — Types of Learning & When to Use Each

**Difficulty:** ⭐ Beginner

**What you'll learn:**
- Supervised vs Unsupervised vs Semi‑supervised vs Reinforcement Learning
- Regression vs Classification vs Clustering vs Dimensionality Reduction
- When to use which approach for a given business problem

**What to read first:**
- 📖 [Google's ML Crash Course — Framing](https://developers.google.com/machine-learning/crash-course/framing/video-lecture) (20 min)
- 📖 [Scikit‑learn: Choosing the Right Estimator](https://scikit-learn.org/stable/tutorial/machine_learning_map/index.html) (cheat sheet)
- 📖 [StatQuest: Machine Learning Fundamentals](https://www.youtube.com/watch?v=Gv9_4yMHFhI) (video, 10 min)

**Task:**
1. Create a markdown document `ml_landscape.md` that maps **15 real‑world problems** to the correct ML type and algorithm family. Examples:
   - "Predict house prices" → Supervised → Regression → Linear Regression / Random Forest
   - "Group customers by buying behaviour" → Unsupervised → Clustering → K‑Means
   - "Detect fraudulent transactions" → Supervised → Classification (imbalanced) → XGBoost + SMOTE
2. For each problem, write one sentence explaining **why** that approach fits.
3. Create a **decision flowchart** (hand‑drawn or Mermaid diagram): "Does the data have labels?" → Yes/No branching → recommended algo family.
4. Pick 3 of the 15 problems. For each, find a free public dataset on Kaggle or UCI ML Repository. Download it, load it in a Jupyter notebook, and print `.shape`, `.dtypes`, `.describe()`, and `.head()`.

**Deliverables:**
1. `/ml_engineer/task1/ml_landscape.md` — 15 problems mapped to ML type + algorithm
2. `/ml_engineer/task1/decision_flowchart.md` — Mermaid or image of the flowchart
3. `/ml_engineer/task1/explore_datasets.ipynb` — notebook exploring 3 datasets
4. `/ml_engineer/task1/dataset_sources.md` — links to the 3 datasets you picked

---

## Task 2: Data Preprocessing & Feature Engineering Pipeline

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- Handling missing values (imputation strategies)
- Encoding categorical variables (One‑Hot, Label, Target encoding)
- Feature scaling (StandardScaler, MinMaxScaler, RobustScaler)
- Feature engineering (creating new features from existing ones)
- Train/test split with stratification

**What to read first:**
- 📖 [Scikit‑learn: Preprocessing Data](https://scikit-learn.org/stable/modules/preprocessing.html) (docs)
- 📖 [Feature Engineering for ML — Google Course](https://developers.google.com/machine-learning/data-prep) (free)
- 📖 [Kaggle: Feature Engineering Micro‑Course](https://www.kaggle.com/learn/feature-engineering) (4 hours)

**Task:**
1. Pick a messy dataset: [Kaggle Titanic](https://www.kaggle.com/c/titanic) or [House Prices](https://www.kaggle.com/c/house-prices-advanced-regression-techniques).
2. Write `preprocess.py` that:
   - Loads raw CSV
   - Profiles the data: % missing per column, data types, unique counts
   - Handles missing values: numeric → median, categorical → mode (make this configurable)
   - Encodes categoricals: try One‑Hot for low‑cardinality, Target Encoding for high‑cardinality
   - Scales numeric features using `StandardScaler`
   - Engineers 3 new features (e.g., `Age * Pclass`, `FamilySize = SibSp + Parch + 1`, `IsAlone = FamilySize == 1`)
   - Splits into train/test (80/20) with stratification on the target
   - Saves `train_processed.csv` and `test_processed.csv`
3. Write `preprocess_report.md` — before vs after comparison: show the same 5 rows raw vs processed, explain each transformation.

**Deliverables:**
1. `/ml_engineer/task2/preprocess.py`
2. `/ml_engineer/task2/preprocess_report.md` — before/after + explanations
3. `/ml_engineer/task2/feature_definitions.yaml` — name, type, source, transformation for each feature
4. `/ml_engineer/task2/requirements.txt`

---

## Task 3: Train Your First Model — Baselines, Metrics & Model Selection

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- Training multiple baseline models and comparing them fairly
- Choosing the right metric: Accuracy vs Precision vs Recall vs F1 vs ROC‑AUC
- Cross‑validation for reliable evaluation
- Confusion matrix interpretation

**What to read first:**
- 📖 [Google ML Crash Course — Classification](https://developers.google.com/machine-learning/crash-course/classification/video-lecture)
- 📖 [StatQuest: Confusion Matrix](https://www.youtube.com/watch?v=Kdsp6soqA7o) (10 min)
- 📖 [StatQuest: ROC and AUC](https://www.youtube.com/watch?v=4jRBRDbJemM) (15 min)
- 📖 [Scikit‑learn: Model Evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)

**Task:**
1. Use the processed data from Task 2 (or re‑process from scratch — each task is independent).
2. Write `train_baselines.py` that:
   - Trains 4 models: Logistic Regression, Decision Tree, Random Forest, Gradient Boosted Trees (XGBoost or sklearn's `GradientBoostingClassifier`)
   - Uses 5‑fold cross‑validation on the training set
   - For each model, computes: Accuracy, Precision, Recall, F1, ROC‑AUC
   - Prints a comparison table to the console
   - Plots a confusion matrix for each model (save as PNGs)
   - Saves the best model as `best_model.pkl` using `joblib`
3. Write `model_comparison.md`:
   - Table: model × metrics
   - Which model won and why
   - Which metric matters most for this problem (and why — e.g., "In fraud detection, recall matters more because missing a fraud is worse than a false alarm")

**Deliverables:**
1. `/ml_engineer/task3/train_baselines.py`
2. `/ml_engineer/task3/model_comparison.md`
3. `/ml_engineer/task3/confusion_matrices/` — 4 PNG files
4. `/ml_engineer/task3/best_model.pkl`

---

## Task 4: Hyperparameter Tuning — Grid Search, Random Search & Optuna

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- What hyperparameters are and why they matter
- Grid Search vs Random Search vs Bayesian Optimization (Optuna)
- How to avoid overfitting during tuning
- Logging experiments for reproducibility

**What to read first:**
- 📖 [Scikit‑learn: Tuning Hyperparameters](https://scikit-learn.org/stable/modules/grid_search.html)
- 📖 [Optuna Documentation — Getting Started](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/001_first.html) (20 min)
- 📖 [StatQuest: Random Forest Hyperparameters](https://www.youtube.com/watch?v=J4Wdy0Wc_xQ) (15 min)

**Task:**
1. Take your best model from Task 3 (or pick XGBoost on any classification dataset).
2. Write `tune.py` that:
   - Defines a hyperparameter search space (at least 4 hyperparameters)
   - Runs **Grid Search** (small grid — 3 values per param) and logs time taken
   - Runs **Random Search** (50 iterations) and logs time taken
   - Runs **Optuna** (50 trials) and logs time taken
   - For each method: saves best params, best CV score, and total time
3. Compare results in `tuning_comparison.md`:
   - Table: method, best_score, time_taken, best_params
   - Which method found the best score? Which was fastest?
   - Your rule of thumb: when to use which method
4. Plot the Optuna optimization history (`optuna.visualization.plot_optimization_history`) and param importances (`plot_param_importances`). Save as PNGs.

**Deliverables:**
1. `/ml_engineer/task4/tune.py`
2. `/ml_engineer/task4/tuning_comparison.md`
3. `/ml_engineer/task4/optuna_history.png` + `optuna_param_importance.png`
4. `/ml_engineer/task4/best_params.json`

---

## Task 5: Regression Deep Dive — Linear Models to Ensemble Methods

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Linear Regression, Ridge, Lasso, Elastic Net
- Polynomial features and regularisation
- Tree‑based regression (Random Forest, XGBoost)
- Evaluation: MAE, RMSE, R², MAPE
- Residual analysis

**What to read first:**
- 📖 [StatQuest: Linear Regression](https://www.youtube.com/watch?v=PaFPbb66DxQ) (27 min)
- 📖 [StatQuest: Ridge vs Lasso](https://www.youtube.com/watch?v=Q81RR3yKn30) (20 min)
- 📖 [Scikit‑learn: Regression](https://scikit-learn.org/stable/modules/linear_model.html)
- 📖 [Kaggle: Intermediate ML](https://www.kaggle.com/learn/intermediate-machine-learning)

**Task:**
1. Pick a regression dataset: [California Housing](https://scikit-learn.org/stable/datasets/real_world.html#california-housing-dataset) or [Kaggle House Prices](https://www.kaggle.com/c/house-prices-advanced-regression-techniques).
2. Write `regression_compare.py` that:
   - Trains 6 models: Linear Regression, Ridge, Lasso, Elastic Net, Random Forest Regressor, XGBoost Regressor
   - Evaluates each with 5‑fold CV: MAE, RMSE, R², MAPE
   - Creates residual plots for top 2 models (predicted vs actual + residual distribution)
3. Write `regression_analysis.md`:
   - Comparison table
   - Residual analysis: are errors random or is there a pattern? What does that mean?
   - When to use linear vs tree‑based for regression

**Deliverables:**
1. `/ml_engineer/task5/regression_compare.py`
2. `/ml_engineer/task5/regression_analysis.md`
3. `/ml_engineer/task5/residual_plots/` — PNGs for top 2 models
4. `/ml_engineer/task5/requirements.txt`

---

## Task 6: Unsupervised Learning — Clustering & Dimensionality Reduction

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- K‑Means, DBSCAN, Hierarchical clustering
- Choosing K (Elbow method, Silhouette score)
- PCA and t‑SNE for visualisation
- Real‑world use: customer segmentation

**What to read first:**
- 📖 [StatQuest: K‑Means Clustering](https://www.youtube.com/watch?v=4b5d3muPQmA) (15 min)
- 📖 [StatQuest: PCA](https://www.youtube.com/watch?v=FgakZw6K1QQ) (20 min)
- 📖 [StatQuest: t‑SNE](https://www.youtube.com/watch?v=NEaUSP4YerM) (12 min)
- 📖 [Scikit‑learn: Clustering](https://scikit-learn.org/stable/modules/clustering.html)

**Task:**
1. Download the [Mall Customer Segmentation](https://www.kaggle.com/vjchoudhary7/customer-segmentation-tutorial-in-r) dataset or use `sklearn.datasets.make_blobs` to generate synthetic clusters.
2. Write `cluster_analysis.py` that:
   - Runs K‑Means with K = 2 to 10, plots Elbow curve and Silhouette scores → pick optimal K
   - Runs DBSCAN with 3 different `eps` values → compare to K‑Means
   - Runs Hierarchical clustering → plot the dendrogram
   - For each method: label each customer, print cluster sizes and cluster centres
3. Apply PCA (reduce to 2D) and t‑SNE (2D) to the dataset. Colour by cluster assignment. Save scatter plots.
4. Write `clustering_report.md`:
   - Which algorithm gave the cleanest clusters? How did you decide?
   - What does each cluster represent? (e.g., "high income + high spending = VIP customers")
   - When to use K‑Means vs DBSCAN vs Hierarchical

**Deliverables:**
1. `/ml_engineer/task6/cluster_analysis.py`
2. `/ml_engineer/task6/clustering_report.md`
3. `/ml_engineer/task6/plots/` — elbow, silhouette, dendrogram, PCA scatter, t‑SNE scatter
4. `/ml_engineer/task6/cluster_profiles.csv` — cluster_id, size, mean_feature1, mean_feature2, ...

---

## Task 7: Model Serialisation & Serving as a REST API

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- Saving and loading models (pickle, joblib, ONNX)
- Building a prediction API with FastAPI
- Request/response validation with Pydantic
- Dockerising the API
- Basic health checks

**What to read first:**
- 📖 [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) (official — first 5 sections)
- 📖 [Docker for Beginners](https://docker-curriculum.com/) (first 3 sections)
- 📖 [Pydantic Docs — Models](https://docs.pydantic.dev/latest/concepts/models/)
- 📖 [Real Python: Model Serving](https://realpython.com/fastapi-python-web-apis/)

**Task:**
1. Take any trained model (from earlier tasks or train a quick one on Iris / Titanic).
2. Write `app.py` using FastAPI with:
   - `POST /predict` — accepts JSON body with features, returns prediction + probability
   - `GET /health` — returns `{"status": "healthy", "model_version": "v1"}`
   - `GET /model-info` — returns model type, features expected, training date
   - Input validation using Pydantic (reject missing fields, wrong types)
3. Write a `Dockerfile` (multi‑stage: build deps → copy model → run API).
4. Build and run the container locally. Test with `curl` or `httpie`:
   - 3 valid requests → should get predictions
   - 2 invalid requests → should get 422 validation errors
5. Write `api_docs.md` — endpoint spec, example curl commands, error handling

**Deliverables:**
1. `/ml_engineer/task7/app.py`
2. `/ml_engineer/task7/Dockerfile`
3. `/ml_engineer/task7/api_docs.md` — endpoint spec + example requests/responses
4. `/ml_engineer/task7/test_requests.sh` — shell script with 5 curl commands
5. `/ml_engineer/task7/requirements.txt`

---

## Task 8: Experiment Tracking with MLflow

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- Why experiment tracking matters
- MLflow: logging params, metrics, artifacts, models
- Comparing runs in the MLflow UI
- Model Registry: staging → production workflow

**What to read first:**
- 📖 [MLflow Quickstart](https://mlflow.org/docs/latest/getting-started/index.html) (30 min)
- 📖 [MLflow Tracking Guide](https://mlflow.org/docs/latest/tracking.html)
- 📖 [Made With ML: Experiment Tracking](https://madewithml.com/courses/mlops/experiment-tracking/) (free)

**Task:**
1. Install MLflow locally: `pip install mlflow`.
2. Write `train_with_tracking.py` that:
   - Creates an MLflow experiment called "my‑first‑experiment"
   - Trains 3 different models (e.g., LogisticRegression, RandomForest, XGBoost) on any classification dataset
   - For each run, logs: all hyperparameters, metrics (accuracy, F1, AUC), the model artifact, training data hash, training time
   - Tags each run with `model_type` and `dataset_name`
3. Open the MLflow UI (`mlflow ui`) and:
   - Compare the 3 runs side‑by‑side
   - Take a screenshot showing the comparison
4. Register the best model in MLflow Model Registry. Transition it to "Staging".
5. Write `load_and_predict.py` — loads the model from MLflow registry and makes a prediction.

**Deliverables:**
1. `/ml_engineer/task8/train_with_tracking.py`
2. `/ml_engineer/task8/load_and_predict.py`
3. `/ml_engineer/task8/mlflow_screenshot.png` — comparison view
4. `/ml_engineer/task8/tracking_notes.md` — what to log, what not to log, naming conventions for experiments

---

## Task 9: Batch Inference Pipeline with Data Validation

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Batch prediction vs real‑time prediction — when to use each
- Data validation before inference (schema checks, drift detection)
- Idempotent pipelines (re‑running doesn't duplicate results)
- Monitoring data quality over time

**What to read first:**
- 📖 [Great Expectations Getting Started](https://docs.greatexpectations.io/docs/tutorials/quickstart/) (30 min)
- 📖 [Google: Data Validation in ML](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning#data_validation) (section)
- 📖 [Evidently AI: Data Drift Detection](https://docs.evidentlyai.com/) (open‑source)

**Task:**
1. Simulate a production scenario: use `faker` to generate 100 rows of "new daily data" with the same schema as your training data, but introduce 10% dirty rows (nulls, wrong types, impossible values).
2. Write `validate.py` that:
   - Checks schema (column names, types)
   - Checks value ranges (e.g., age between 0–120, no negative prices)
   - Detects nulls and duplicates
   - Runs a distribution drift check (compare new data stats vs training data stats using KS test)
   - Outputs a validation report: PASS/FAIL per check, with details
3. Write `batch_predict.py` that:
   - Reads new data from `data/incoming/batch_<date>.csv`
   - Runs `validate.py` checks first — if FAIL, logs and skips
   - Loads a pre‑trained model
   - Generates predictions
   - Appends to `data/predictions/preds_<date>.csv` (idempotent — doesn't re‑predict if already done)
4. Run for 5 simulated days. Show the validation report for a clean day and a dirty day.

**Deliverables:**
1. `/ml_engineer/task9/validate.py`
2. `/ml_engineer/task9/batch_predict.py`
3. `/ml_engineer/task9/generate_fake_data.py` — data simulator
4. `/ml_engineer/task9/validation_reports/` — 5 daily reports
5. `/ml_engineer/task9/batch_pipeline_notes.md` — when to use batch vs real‑time, idempotency tips

---

## Task 10: End‑to‑End ML Pipeline with CI/CD (GitHub Actions)

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Structuring an ML project for CI/CD
- Automated testing for ML code (unit tests + data tests + model tests)
- Validation gates: new model must beat the current one
- GitHub Actions for ML pipelines

**What to read first:**
- 📖 [Made With ML: CI/CD for ML](https://madewithml.com/courses/mlops/cicd/) (free)
- 📖 [GitHub Actions Quickstart](https://docs.github.com/en/actions/quickstart)
- 📖 [Testing ML Models — Thoughtworks](https://martinfowler.com/articles/cd4ml.html#TestingAndQualityInMachineLearning)

**Task:**
1. Structure a repo:
   ```
   ml_project/
   ├── .github/workflows/ml_pipeline.yml
   ├── src/train.py, predict.py, evaluate.py
   ├── tests/test_data.py, test_model.py
   ├── config/thresholds.yaml
   └── requirements.txt
   ```
2. Write unit tests:
   - `test_data.py`: check data has expected columns, no nulls in critical fields, correct split ratio
   - `test_model.py`: check model output shape, predictions are within valid range, model loads without error
3. Write `thresholds.yaml`: minimum acceptable F1 (e.g., 0.75), maximum inference latency (e.g., 100ms), allowed degradation vs current model (e.g., −0.02).
4. Write `ml_pipeline.yml` that on push to `main`:
   - Installs deps + runs linter (flake8)
   - Runs pytest
   - Trains model on small sample (fast smoke test)
   - Evaluates model against thresholds
   - If pass → logs success. If fail → logs failure with reason.
5. Push to GitHub, trigger the pipeline, take a screenshot of a passing run.

**Deliverables:**
1. `/ml_engineer/task10/.github/workflows/ml_pipeline.yml`
2. `/ml_engineer/task10/tests/test_data.py` + `test_model.py`
3. `/ml_engineer/task10/config/thresholds.yaml`
4. `/ml_engineer/task10/cicd_notes.md` — what you'd add next (model registry integration, staging deploy, rollback)
5. `/ml_engineer/task10/pipeline_screenshot.png` — GitHub Actions run

---

## Learning Path Summary

| Task | Topic | Difficulty | Key Tools |
|------|-------|-----------|-----------|
| 1 | ML Landscape & Problem Framing | ⭐ | Markdown, Jupyter |
| 2 | Data Preprocessing & Feature Engineering | ⭐⭐ | Pandas, Scikit‑learn |
| 3 | Model Training & Evaluation | ⭐⭐ | Scikit‑learn, XGBoost |
| 4 | Hyperparameter Tuning | ⭐⭐⭐ | Optuna, Scikit‑learn |
| 5 | Regression Deep Dive | ⭐⭐⭐ | Scikit‑learn, XGBoost |
| 6 | Clustering & Dimensionality Reduction | ⭐⭐⭐ | Scikit‑learn, Matplotlib |
| 7 | Model Serving (FastAPI + Docker) | ⭐⭐⭐⭐ | FastAPI, Docker, Pydantic |
| 8 | Experiment Tracking (MLflow) | ⭐⭐⭐⭐ | MLflow |
| 9 | Batch Inference & Data Validation | ⭐⭐⭐⭐⭐ | Great Expectations, Faker |
| 10 | CI/CD for ML | ⭐⭐⭐⭐⭐ | GitHub Actions, pytest |

**All tools are free and open‑source. No paid cloud services required.**
