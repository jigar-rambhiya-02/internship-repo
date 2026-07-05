# Data Scientist — 10 Tasks (Beginner → 2‑Year Experience)

> **Goal:** Go from "I know Python" to "I can extract insights from data, design experiments, build predictive models, and communicate results to drive business decisions."
> A Data Scientist sits at the intersection of statistics, ML, and business — you find patterns, test hypotheses, and tell data stories.
> Each task is self‑contained. Difficulty increases from Task 1 → 10.

---

## Task 1: Exploratory Data Analysis (EDA) — Tell a Story with Data

**Difficulty:** ⭐ Beginner

**What you'll learn:**
- Systematic EDA workflow: shape, types, distributions, correlations
- Univariate, bivariate, and multivariate analysis
- Identifying data quality issues through visualisation
- Using plots to form hypotheses before modelling

**What to read first:**
- 📖 [Kaggle: Data Visualisation Micro‑Course](https://www.kaggle.com/learn/data-visualization) (4 hours, free)
- 📖 [Python Graph Gallery](https://www.python-graph-gallery.com/) — visual catalogue of plot types
- 📖 [Towards Data Science: EDA with Pandas Profiling](https://towardsdatascience.com/exploratory-data-analysis-with-pandas-profiling-de3aae2ddff3) (10 min read)
- 📖 [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html) (official docs)

**Task:**
1. Pick a dataset with at least 10 columns and 5,000+ rows: [Kaggle Spaceship Titanic](https://www.kaggle.com/competitions/spaceship-titanic), [NYC Airbnb](https://www.kaggle.com/dgomonov/new-york-city-airbnb-open-data), or [Online Retail](https://archive.ics.uci.edu/ml/datasets/online+retail).
2. Write `eda.py` (or a Jupyter notebook `eda.ipynb`) that:
   - Prints data shape, dtypes, `describe()`, null counts, duplicate counts
   - Creates **10 visualisations** covering: histogram, boxplot, scatter plot, heatmap (correlation matrix), bar chart (top categories), violin plot, pair plot (top 5 numeric cols), count plot, line chart (if time‑based), and a stacked/grouped bar chart
   - Each plot must have a title, axis labels, and a 1–2 sentence annotation explaining the insight
3. Write `eda_report.md` summarising:
   - 5 key insights you discovered (e.g., "80% of revenue comes from 15% of customers")
   - 3 data quality issues found (nulls, outliers, inconsistencies)
   - 3 hypotheses to test with further analysis

**Deliverables:**
1. `/data_scientist/task1/eda.py` (or `eda.ipynb`)
2. `/data_scientist/task1/eda_report.md` — insights + hypotheses
3. `/data_scientist/task1/plots/` — 10 saved PNG visualisations
4. `/data_scientist/task1/requirements.txt`

---

## Task 2: Statistics for Data Science — Distributions, Confidence Intervals & Hypothesis Testing

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- Probability distributions: Normal, Binomial, Poisson, Exponential
- Central Limit Theorem (CLT) and why it matters
- Confidence intervals: construction and interpretation
- Hypothesis testing: t‑tests, chi‑squared tests, p‑values, significance levels
- Type I and Type II errors

**What to read first:**
- 📖 [StatQuest: p‑Values Clearly Explained](https://www.youtube.com/watch?v=vemZtEM63GY) (11 min)
- 📖 [Khan Academy: Confidence Intervals](https://www.khanacademy.org/math/statistics-probability/confidence-intervals-one-sample) (free course)
- 📖 [StatQuest: Hypothesis Testing](https://www.youtube.com/watch?v=0oc49DyA3hU) (14 min)
- 📖 [SciPy Stats Documentation](https://docs.scipy.org/doc/scipy/reference/stats.html)

**Task:**
1. Write `distributions_demo.py` that:
   - Generates samples from Normal, Binomial, Poisson, and Exponential distributions (1,000 samples each)
   - Plots each distribution as a histogram with a fitted curve overlay
   - Demonstrates the CLT: take 1,000 samples of size 30 from a skewed distribution (e.g., Exponential), compute the mean of each sample, and plot the distribution of means → shows it approaches Normal
2. Write `hypothesis_tests.py` using a real dataset (e.g., Titanic):
   - Two‑sample t‑test: "Is the average fare for survivors significantly different from non‑survivors?"
   - Chi‑squared test: "Is survival independent of passenger class?"
   - One‑sample t‑test: "Is the average age significantly different from 30?"
   - For each test: state H₀ and H₁, compute the test statistic, p‑value, and conclusion at α = 0.05
3. Write `stats_report.md`:
   - Results table: test, H₀, p‑value, conclusion
   - Explain in plain English what each result means for a non‑technical stakeholder
   - Explain: when would you use a t‑test vs a chi‑squared test vs Mann‑Whitney U?

**Deliverables:**
1. `/data_scientist/task2/distributions_demo.py`
2. `/data_scientist/task2/hypothesis_tests.py`
3. `/data_scientist/task2/stats_report.md`
4. `/data_scientist/task2/plots/` — distribution plots + CLT demo
5. `/data_scientist/task2/requirements.txt`

---

## Task 3: Advanced Visualisation & Dashboard Building

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- Advanced Matplotlib and Seaborn customisation
- Interactive dashboards with Plotly and Streamlit
- Choosing the right chart for the data type and audience
- Dashboard design principles: clarity over complexity

**What to read first:**
- 📖 [Plotly Express Tutorial](https://plotly.com/python/plotly-express/) (docs)
- 📖 [Streamlit Getting Started](https://docs.streamlit.io/get-started) (30 min)
- 📖 [Storytelling with Data — Blog](https://www.storytellingwithdata.com/blog) (principles)
- 📖 [From Data to Viz](https://www.data-to-viz.com/) — decision tree for chart types

**Task:**
1. Pick a multi‑dimensional dataset: [Gapminder](https://www.gapminder.org/data/), [WHO Global Health](https://www.who.int/data/gho), or the Online Retail dataset.
2. Write `interactive_plots.py` using Plotly:
   - Animated scatter plot (like Gapminder: x=GDP, y=LifeExpectancy, size=Population, color=Continent, frame=Year)
   - Choropleth map (colour countries by a metric)
   - Sunburst chart (hierarchical category breakdown)
   - Treemap (alternative hierarchical view)
3. Write `dashboard.py` using Streamlit that:
   - Has a sidebar with filters (date range, category dropdowns, numeric sliders)
   - Shows 4 KPI cards at the top (e.g., Total Revenue, Avg Order Value, Total Customers, Growth %)
   - Displays 4 interactive charts (line, bar, pie, scatter) that update based on filters
   - Has a data table with search/sort functionality
4. Take 3 screenshots of the dashboard with different filter combinations.

**Deliverables:**
1. `/data_scientist/task3/interactive_plots.py` — 4 Plotly visualisations
2. `/data_scientist/task3/dashboard.py` — Streamlit dashboard
3. `/data_scientist/task3/screenshots/` — 3 dashboard screenshots
4. `/data_scientist/task3/chart_selection_guide.md` — when to use which chart type (table with 10+ chart types)
5. `/data_scientist/task3/requirements.txt`

---

## Task 4: A/B Testing — Design, Analyse & Report

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Designing a proper A/B test: control/treatment, sample size, power analysis
- Calculating minimum sample size for statistical power
- Analysing results: z‑test for proportions, t‑test for means
- Understanding practical significance vs statistical significance
- Common pitfalls: peeking, novelty effect, Simpson's paradox

**What to read first:**
- 📖 [Evan Miller: How Not to Run an A/B Test](https://www.evanmiller.org/how-not-to-run-an-ab-test.html) (15 min — essential)
- 📖 [Evan Miller: Sample Size Calculator](https://www.evanmiller.org/ab-testing/sample-size.html) (interactive)
- 📖 [StatQuest: Statistical Power](https://www.youtube.com/watch?v=Rsc5znwR5FA) (15 min)
- 📖 [Udacity: A/B Testing (Free Course)](https://www.udacity.com/course/ab-testing--ud257)

**Task:**
1. Write `ab_test_design.py` that:
   - Takes as input: baseline conversion rate (e.g., 10%), minimum detectable effect (e.g., 2%), significance level (0.05), power (0.80)
   - Calculates the minimum sample size per group
   - Outputs a test design document: duration estimate (given daily traffic), groups, metric definitions
2. Simulate an A/B test in `ab_test_simulate.py`:
   - Generate synthetic data: Group A (control, n=5000, conversion=10%) and Group B (treatment, n=5000, conversion=12%)
   - Run a z‑test for proportions → compute p‑value and confidence interval for the difference
   - Run a chi‑squared test → compare to the z‑test result
   - Visualise: conversion rate bar chart with error bars, cumulative conversion over time (both groups)
3. Simulate a case where the test has **no real effect** (both groups 10%). Show that the test correctly fails to reject H₀.
4. Write `ab_test_report.md`:
   - Executive summary (1 paragraph for a non‑technical stakeholder)
   - Detailed results with charts
   - Recommendation: ship or don't ship, and why
   - Discuss 3 pitfalls you avoided

**Deliverables:**
1. `/data_scientist/task4/ab_test_design.py`
2. `/data_scientist/task4/ab_test_simulate.py`
3. `/data_scientist/task4/ab_test_report.md` — executive summary + detailed results
4. `/data_scientist/task4/plots/` — conversion charts, cumulative plots
5. `/data_scientist/task4/requirements.txt`

---

## Task 5: SQL for Data Science — Querying, Aggregations & Window Functions

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Complex SQL queries: JOINs, subqueries, CTEs
- Aggregations and GROUP BY with HAVING
- Window functions: ROW_NUMBER, RANK, LAG, LEAD, running totals
- Writing analytical queries that answer business questions

**What to read first:**
- 📖 [Mode Analytics: SQL Tutorial (Advanced)](https://mode.com/sql-tutorial/) (free, excellent)
- 📖 [SQLBolt: Interactive SQL Lessons](https://sqlbolt.com/) (beginner → intermediate)
- 📖 [Window Functions Explained](https://mode.com/sql-tutorial/sql-window-functions/) (Mode Analytics)
- 📖 [DuckDB Getting Started](https://duckdb.org/docs/guides/overview.html) (in‑process SQL engine)

**Task:**
1. Load the [Online Retail dataset](https://archive.ics.uci.edu/ml/datasets/online+retail) into a SQLite or DuckDB database.
2. Write `analytics_queries.sql` with 10 business queries:
   - Total revenue by country (top 10)
   - Monthly revenue trend
   - Customer with highest lifetime value
   - Products frequently bought together (co‑occurrence using self‑join)
   - Customer cohort analysis: retention by first‑purchase month (using window functions)
   - Revenue per customer percentile (using NTILE)
   - Month‑over‑month growth rate (using LAG)
   - RFM segmentation: Recency, Frequency, Monetary scores per customer
   - Moving 3‑month average revenue (window function)
   - Top 5 products per country (using RANK + partitioning)
3. Write `run_queries.py` that:
   - Creates the database from CSV
   - Executes each query and saves results as CSVs
   - Prints formatted tables to the console
4. Write `sql_insights.md` — for each query, state the business question, the SQL approach, and the insight.

**Deliverables:**
1. `/data_scientist/task5/analytics_queries.sql` — 10 queries with comments
2. `/data_scientist/task5/run_queries.py`
3. `/data_scientist/task5/sql_insights.md` — question + insight per query
4. `/data_scientist/task5/query_results/` — 10 CSV files
5. `/data_scientist/task5/requirements.txt`

---

## Task 6: Time Series Analysis & Forecasting

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Time series components: trend, seasonality, noise
- Stationarity and how to test for it (ADF test)
- Decomposition: additive vs multiplicative
- Forecasting: ARIMA, SARIMA, Prophet
- Evaluation: MAE, RMSE, MAPE on a time‑hold‑out

**What to read first:**
- 📖 [Kaggle: Time Series Course](https://www.kaggle.com/learn/time-series) (free, 5 lessons)
- 📖 [StatQuest: Time Series Concepts](https://www.youtube.com/watch?v=nGkEKbhdVmY) (15 min)
- 📖 [Prophet Documentation](https://facebook.github.io/prophet/docs/quick_start.html) (Meta, open‑source)
- 📖 [Statsmodels: Time Series](https://www.statsmodels.org/stable/tsa.html)

**Task:**
1. Pick a time series dataset: [Kaggle Store Sales](https://www.kaggle.com/competitions/store-sales-time-series-forecasting), [Daily Climate Data](https://www.kaggle.com/datasets/sumanthvrao/daily-climate-time-series-data), or use the retail dataset's daily revenue.
2. Write `ts_analysis.py` that:
   - Plots the raw time series
   - Decomposes into trend, seasonality, and residual (additive + multiplicative)
   - Tests for stationarity (ADF test) — if non‑stationary, apply differencing until stationary
   - Plots ACF and PACF to determine ARIMA parameters (p, d, q)
3. Write `ts_forecast.py` that:
   - Splits data into train (80%) and test (20%) chronologically — **no random splitting**
   - Trains 3 models: ARIMA (manual params), auto‑ARIMA (using `pmdarima`), and Prophet
   - Forecasts the test period
   - Plots actual vs predicted for each model
   - Computes MAE, RMSE, MAPE for each
4. Write `ts_report.md`:
   - Comparison table of model performance
   - Which model won and why?
   - What patterns did the decomposition reveal?
   - When to use ARIMA vs Prophet (rule of thumb)

**Deliverables:**
1. `/data_scientist/task6/ts_analysis.py` — decomposition + stationarity tests
2. `/data_scientist/task6/ts_forecast.py` — 3 models compared
3. `/data_scientist/task6/ts_report.md`
4. `/data_scientist/task6/plots/` — raw series, decomposition, ACF/PACF, forecast comparisons
5. `/data_scientist/task6/requirements.txt`

---

## Task 7: Feature Selection & Dimensionality Reduction for Modelling

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- Filter methods: correlation, mutual information, variance threshold
- Wrapper methods: forward selection, backward elimination, RFE
- Embedded methods: L1 regularisation (Lasso), tree feature importance
- PCA for dimensionality reduction in modelling pipelines
- The curse of dimensionality

**What to read first:**
- 📖 [Scikit‑learn: Feature Selection](https://scikit-learn.org/stable/modules/feature_selection.html) (docs)
- 📖 [StatQuest: Regularisation — Ridge vs Lasso](https://www.youtube.com/watch?v=Q81RR3yKn30) (20 min)
- 📖 [Machine Learning Mastery: Feature Selection](https://machinelearningmastery.com/feature-selection-with-real-and-categorical-data/) (tutorial)
- 📖 [StatQuest: PCA Step by Step](https://www.youtube.com/watch?v=FgakZw6K1QQ) (20 min)

**Task:**
1. Use a high‑dimensional dataset (20+ features): [Kaggle House Prices](https://www.kaggle.com/c/house-prices-advanced-regression-techniques) or [Credit Card Default](https://archive.ics.uci.edu/ml/datasets/default+of+credit+card+clients).
2. Write `feature_selection.py` that:
   - Computes and plots the correlation matrix — identify highly correlated pairs (>0.85)
   - Runs Variance Threshold filter — remove near‑zero‑variance features
   - Runs Mutual Information scores — rank features
   - Runs RFE (Recursive Feature Elimination) with a Random Forest — select top 10
   - Runs Lasso with increasing alpha — plot number of non‑zero coefficients vs alpha
   - Compares: train a model with all features vs top‑10 from each method → accuracy table
3. Write `pca_analysis.py` that:
   - Applies PCA to the dataset
   - Plots the explained variance ratio (scree plot) — pick the number of components that capture 95% variance
   - Trains a model on PCA‑reduced data vs original — compare performance
4. Write `feature_selection_report.md`:
   - Table: method → selected features → model score
   - Did fewer features hurt or help? By how much?
   - Your recommendation: which method to use when

**Deliverables:**
1. `/data_scientist/task7/feature_selection.py`
2. `/data_scientist/task7/pca_analysis.py`
3. `/data_scientist/task7/feature_selection_report.md`
4. `/data_scientist/task7/plots/` — correlation heatmap, scree plot, Lasso path, RFE ranking
5. `/data_scientist/task7/requirements.txt`

---

## Task 8: Causal Inference — Moving Beyond Correlation

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- Correlation ≠ causation — and what to do about it
- Propensity Score Matching (PSM)
- Difference‑in‑Differences (DiD)
- Instrumental Variables (IV) — concept + simple example
- When you can and can't make causal claims from observational data

**What to read first:**
- 📖 [Brady Neal: Introduction to Causal Inference (Free Course)](https://www.bradyneal.com/causal-inference-course) (chapters 1–5)
- 📖 [Matheus Facure: Causal Inference for the Brave and True](https://matheusfacure.github.io/python-causality-handbook/) (free online book — chapters 1–7)
- 📖 [Scott Cunningham: Causal Inference — The Mixtape](https://mixtape.scunning.com/) (free online book)
- 📖 [DoWhy Documentation](https://www.pywhy.org/dowhy/v0.11.1/) (Microsoft, open‑source)

**Task:**
1. Use a dataset where treatment isn't random: [LaLonde Jobs Training Dataset](https://users.nber.org/~rdehejia/data/.nswdata2.html) or simulate one.
2. Write `propensity_matching.py` that:
   - Estimates propensity scores using Logistic Regression (probability of receiving treatment)
   - Matches treated to control using nearest‑neighbour matching on propensity scores
   - Before matching: show the covariate imbalance (standardised mean differences)
   - After matching: show the covariate balance improved
   - Estimate the Average Treatment Effect (ATE) on the matched sample
3. Write `diff_in_diff.py` that:
   - Simulates or uses a dataset with pre/post and treated/control groups
   - Estimates the DiD effect using a regression: `outcome ~ treated + post + treated*post`
   - Plots the parallel trends (pre‑treatment period) and the divergence (post‑treatment)
   - Tests the parallel trends assumption
4. Write `causal_report.md`:
   - Plain‑English explanation: what is the causal question? What method did you use?
   - Results: ATE from PSM, DiD estimate, confidence intervals
   - Limitations: what assumptions are you making? What could invalidate the results?
   - Decision tree: when to use PSM vs DiD vs RCT

**Deliverables:**
1. `/data_scientist/task8/propensity_matching.py`
2. `/data_scientist/task8/diff_in_diff.py`
3. `/data_scientist/task8/causal_report.md`
4. `/data_scientist/task8/plots/` — balance plots, parallel trends, DiD visualisation
5. `/data_scientist/task8/requirements.txt`

---

## Task 9: End‑to‑End Data Science Project — From Question to Stakeholder Presentation

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Structuring a complete DS project: business question → data → analysis → model → insight → presentation
- Model interpretability: SHAP values, partial dependence plots
- Creating a non‑technical stakeholder presentation from technical results
- Writing a reproducible analysis notebook with narrative

**What to read first:**
- 📖 [SHAP Documentation](https://shap.readthedocs.io/en/latest/) (Lundberg, open‑source)
- 📖 [Interpretable ML Book — Christoph Molnar](https://christophm.github.io/interpretable-ml-book/) (free, chapters 5–9)
- 📖 [Google: ML Fairness](https://developers.google.com/machine-learning/fairness-overview) (overview)
- 📖 [Kaggle: ML Explainability Course](https://www.kaggle.com/learn/machine-learning-explainability) (free)

**Task:**
1. Pick a business problem: "Predict customer churn for a telecom company" using [Kaggle Telco Churn](https://www.kaggle.com/blastchar/telco-customer-churn) or "Predict loan default" using [Kaggle Lending Club](https://www.kaggle.com/wordsforthewise/lending-club).
2. Write a complete analysis notebook `analysis.ipynb`:
   - Section 1: Business Context (what problem? why does it matter? what's the cost of errors?)
   - Section 2: Data Understanding (EDA — 5+ plots with insights)
   - Section 3: Feature Engineering + Preprocessing
   - Section 4: Modelling (3+ models, cross‑validated, comparison table)
   - Section 5: Interpretability (SHAP summary plot, SHAP force plot for 3 individual predictions, partial dependence for top 3 features)
   - Section 6: Business Recommendations (actionable — e.g., "Target customers with >$100 monthly charges and month‑to‑month contracts for retention offers")
3. Write `stakeholder_summary.md` — a 1‑page non‑technical summary:
   - The problem in plain English
   - Key findings (3 bullet points)
   - Recommended actions (3 bullet points)
   - Expected impact (e.g., "Reducing churn by 5% = $X,000/month saved")
4. Export 5 key plots as standalone PNGs for use in presentations.

**Deliverables:**
1. `/data_scientist/task9/analysis.ipynb` — full narrative notebook
2. `/data_scientist/task9/stakeholder_summary.md` — 1‑page non‑technical summary
3. `/data_scientist/task9/key_plots/` — 5 PNGs (SHAP summary, top features, churn by segment, etc.)
4. `/data_scientist/task9/model_card.md` — model type, training data, performance, limitations, ethical considerations
5. `/data_scientist/task9/requirements.txt`

---

## Task 10: Bayesian Data Analysis — Thinking in Distributions, Not Point Estimates

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Bayesian vs Frequentist: philosophical and practical differences
- Bayes' Theorem applied: prior → likelihood → posterior
- Bayesian A/B testing: probability that B is better than A (not just p‑values)
- Markov Chain Monte Carlo (MCMC) basics with PyMC
- Communicating uncertainty with credible intervals

**What to read first:**
- 📖 [Bayesian Methods for Hackers (Free Book)](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers) (chapters 1–3)
- 📖 [StatQuest: Bayes' Theorem](https://www.youtube.com/watch?v=9wCnvr7Xw4E) (15 min)
- 📖 [PyMC Getting Started](https://www.pymc.io/projects/docs/en/stable/learn.html) (open‑source)
- 📖 [Think Bayes — Allen Downey (Free)](https://allendowney.github.io/ThinkBayes2/) (chapters 1–6)

**Task:**
1. Write `bayesian_ab_test.py`:
   - Simulate an A/B test: Group A (1,000 visitors, 100 conversions), Group B (1,000 visitors, 130 conversions)
   - Use Beta distributions as priors (Beta(1,1) = uninformative)
   - Compute the posterior distributions for both groups
   - Plot both posteriors on the same chart
   - Compute: P(B > A) using Monte Carlo simulation (draw 100,000 samples from each posterior)
   - Compute the expected lift and its 95% credible interval
   - Compare to a frequentist z‑test on the same data
2. Write `bayesian_regression.py` using PyMC:
   - Load a simple dataset (e.g., advertising spend vs sales)
   - Define a Bayesian linear regression: `sales ~ Normal(α + β*spend, σ)`
   - Set weakly informative priors
   - Run MCMC (2,000 samples, 4 chains)
   - Plot the posterior distributions for α, β, σ
   - Plot the posterior predictive: many regression lines overlaid on the data (shows uncertainty)
   - Compare the Bayesian coefficient estimates to sklearn's OLS
3. Write `bayesian_report.md`:
   - When is Bayesian analysis better than frequentist? (3 concrete scenarios)
   - Explain: what does "95% credible interval" mean vs "95% confidence interval"?
   - Your results: P(B > A), expected lift, comparison to frequentist
   - Posterior predictive checks: does the model fit the data well?

**Deliverables:**
1. `/data_scientist/task10/bayesian_ab_test.py`
2. `/data_scientist/task10/bayesian_regression.py`
3. `/data_scientist/task10/bayesian_report.md`
4. `/data_scientist/task10/plots/` — posterior distributions, posterior predictive, comparison charts
5. `/data_scientist/task10/requirements.txt`

---

## Learning Path Summary

| Task | Topic | Difficulty | Key Tools |
|------|-------|-----------|-----------|
| 1 | Exploratory Data Analysis | ⭐ | Pandas, Seaborn, Matplotlib |
| 2 | Statistics & Hypothesis Testing | ⭐⭐ | SciPy, NumPy |
| 3 | Interactive Visualisation & Dashboards | ⭐⭐ | Plotly, Streamlit |
| 4 | A/B Testing | ⭐⭐⭐ | SciPy, Statsmodels |
| 5 | SQL for Analytics | ⭐⭐⭐ | SQLite/DuckDB, SQL |
| 6 | Time Series Forecasting | ⭐⭐⭐ | Statsmodels, Prophet, pmdarima |
| 7 | Feature Selection & Dimensionality Reduction | ⭐⭐⭐⭐ | Scikit‑learn |
| 8 | Causal Inference | ⭐⭐⭐⭐ | DoWhy, Statsmodels |
| 9 | End‑to‑End DS Project + Interpretability | ⭐⭐⭐⭐⭐ | SHAP, Scikit‑learn |
| 10 | Bayesian Data Analysis | ⭐⭐⭐⭐⭐ | PyMC, ArviZ |

**All tools are free and open‑source. No paid cloud services required.**
