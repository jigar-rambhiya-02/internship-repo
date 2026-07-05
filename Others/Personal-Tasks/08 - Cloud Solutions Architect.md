# Cloud Solutions Architect (AI/ML Focus) — 10 Tasks (Beginner → 2‑Year Experience)

> **Goal:** Go from "I know Python and basic ML" to "I can design, cost, and architect cloud‑based AI/ML systems that are secure, scalable, and production‑ready."
> A Cloud Solutions Architect (AI/ML) designs the infrastructure and system architecture for ML workloads — you make technical choices that affect cost, performance, reliability, and team velocity.
> Each task is self‑contained. Difficulty increases from Task 1 → 10.

---

## Task 1: Cloud Computing Fundamentals — Services, Pricing & the AI/ML Stack

**Difficulty:** ⭐ Beginner

**What you'll learn:**
- Cloud service models: IaaS, PaaS, SaaS, and where ML fits
- Core cloud services mapped to ML needs: compute, storage, networking, databases
- Cloud pricing models: on‑demand, spot/preemptible, reserved
- The ML‑specific service stack across providers (at a conceptual level)

**What to read first:**
- 📖 [Google Cloud: Cloud Computing Fundamentals](https://cloud.google.com/learn/what-is-cloud-computing) (overview)
- 📖 [AWS: Cloud Concepts](https://aws.amazon.com/getting-started/cloud-essentials/) (overview)
- 📖 [Azure: Cloud Adoption Framework](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/) (overview)
- 📖 [LocalStack: Cloud Emulation](https://docs.localstack.cloud/getting-started/) (free local cloud simulation)

**Task:**
1. Write `cloud_service_map.md`:
   - Create a comprehensive mapping table: ML Need → Cloud Service Category → GCP Service → AWS Service → Azure Service → Free/Local Alternative. Cover:
     - Compute (training): VMs, GPUs, TPUs → local machine, Google Colab
     - Compute (serving): serverless, containers → Docker + FastAPI locally
     - Storage (data): object storage, file systems → local filesystem, MinIO
     - Storage (models): model registry → MLflow locally
     - Databases: SQL, NoSQL, vector DBs → SQLite, DuckDB, ChromaDB
     - Orchestration: managed Airflow, Step Functions → Airflow locally
     - Monitoring: CloudWatch, Cloud Monitoring → Prometheus + Grafana locally
     - ML Platform: SageMaker, Vertex AI, Azure ML → MLflow + FastAPI + Docker
2. Write `pricing_calculator.py`:
   - For a given ML workload (training hours, serving requests/day, storage GB, data transfer), estimate the monthly cost on:
     - On‑demand pricing
     - Spot/preemptible pricing (70% discount estimate)
     - Reserved pricing (40% discount estimate)
   - Use realistic pricing tiers (hardcoded from public pricing pages)
   - Scenario: "Train a model for 100 GPU hours, serve 1M requests/month, store 500GB"
3. Write `local_cloud_setup.md`:
   - List of tools that simulate cloud services locally:
     - MinIO (S3‑compatible storage)
     - LocalStack (AWS service emulation)
     - DuckDB (BigQuery/Redshift alternative)
     - Docker + Kind (Kubernetes locally)
     - MLflow (Vertex AI/SageMaker alternative)
   - Step‑by‑step: set up MinIO locally as your "cloud storage"

**Deliverables:**
1. `/cloud_architect/task1/cloud_service_map.md` — comprehensive mapping table
2. `/cloud_architect/task1/pricing_calculator.py`
3. `/cloud_architect/task1/local_cloud_setup.md` — local alternatives + setup guide
4. `/cloud_architect/task1/requirements.txt`

---

## Task 2: Infrastructure as Code — Terraform Fundamentals

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- Infrastructure as Code (IaC) concepts: why manual setup is dangerous
- Terraform basics: providers, resources, variables, outputs, state
- Writing and planning infrastructure changes
- Using Terraform with local providers (Docker, local files) — no cloud account needed

**What to read first:**
- 📖 [Terraform: Getting Started (Docker Provider)](https://developer.hashicorp.com/terraform/tutorials/docker-get-started) (free, no cloud needed)
- 📖 [Terraform: Introduction to IaC](https://developer.hashicorp.com/terraform/intro) (concepts)
- 📖 [Gruntwork: Comprehensive Guide to Terraform](https://blog.gruntwork.io/a-comprehensive-guide-to-terraform-b3d32832baca) (practical)
- 📖 [Pulumi: IaC Comparison](https://www.pulumi.com/docs/concepts/vs/terraform/) (alternative perspective)

**Task:**
1. Install Terraform and write Terraform configs that provision local resources:
   - `main.tf`: Use the Docker provider to create:
     - A Docker network
     - A container running your ML API (from earlier tasks or a simple Flask/FastAPI app)
     - A container running MinIO (S3‑compatible storage)
     - A container running an MLflow tracking server
   - `variables.tf`: Parameterise: image tags, container names, ports, resource limits
   - `outputs.tf`: Output the container IPs, ports, and access URLs
2. Write `terraform.tfvars` for two environments:
   - `dev.tfvars`: minimal resources, single replica
   - `prod.tfvars`: more resources, multiple considerations
3. Demonstrate the Terraform workflow:
   - `terraform init` → `terraform plan` → `terraform apply`
   - Make a change (update image tag) → `terraform plan` (show the diff) → `terraform apply`
   - `terraform destroy` → clean up
4. Write `iac_guide.md`:
   - Why IaC > manual setup (5 reasons with examples)
   - Terraform state: what it is, why it matters, remote state concepts
   - Terraform vs Docker Compose: when to use each
   - Best practices: modules, naming conventions, state management

**Deliverables:**
1. `/cloud_architect/task2/main.tf`, `variables.tf`, `outputs.tf`
2. `/cloud_architect/task2/dev.tfvars`, `prod.tfvars`
3. `/cloud_architect/task2/iac_guide.md` — IaC concepts + best practices
4. `/cloud_architect/task2/terraform_demo.md` — screenshots/logs of plan, apply, destroy
5. `/cloud_architect/task2/requirements.txt`

---

## Task 3: Networking & Security Fundamentals for ML Systems

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- Networking basics: VPCs, subnets, firewalls, DNS, load balancers
- Security: authentication, authorisation, encryption, secrets management
- API security: API keys, JWT tokens, rate limiting
- Securing ML endpoints: input validation, model extraction prevention

**What to read first:**
- 📖 [OWASP: API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) (essential)
- 📖 [FastAPI: Security Tutorial](https://fastapi.tiangolo.com/tutorial/security/) (OAuth2, JWT)
- 📖 [HashiCorp Vault: Getting Started](https://developer.hashicorp.com/vault/tutorials/getting-started) (secrets management)
- 📖 [Docker: Network Drivers](https://docs.docker.com/engine/network/) (container networking)

**Task:**
1. Write `secure_api.py` (FastAPI) that adds security to an ML prediction endpoint:
   - API key authentication (check `X-API-Key` header)
   - JWT token authentication (login endpoint → returns token → use token for predictions)
   - Rate limiting (10 requests/minute per API key using a simple in‑memory counter)
   - Input validation: reject suspiciously large payloads, validate feature ranges
   - Request logging: log who accessed what, when, from where (IP)
   - CORS configuration
2. Write `security_test.py`:
   - Test: valid API key → 200
   - Test: missing API key → 401
   - Test: expired JWT → 401
   - Test: rate limit exceeded → 429
   - Test: malformed input → 422
   - Test: oversized payload → 413
3. Write `secrets_management.py`:
   - Demonstrate 3 approaches to managing secrets:
     - Environment variables (simplest)
     - `.env` file with `python-dotenv` (development)
     - HashiCorp Vault (production concept — simulate with a local Vault dev server or mock)
   - Show: never commit secrets to Git (.gitignore, pre‑commit hooks)
4. Write `network_architecture.md`:
   - Diagram: internet → load balancer → API gateway → ML service → model storage → database
   - Explain each component's role
   - Security checklist for ML APIs (15 items)
   - Network isolation: why the model storage shouldn't be publicly accessible

**Deliverables:**
1. `/cloud_architect/task3/secure_api.py`
2. `/cloud_architect/task3/security_test.py`
3. `/cloud_architect/task3/secrets_management.py`
4. `/cloud_architect/task3/network_architecture.md` — diagram + security checklist
5. `/cloud_architect/task3/requirements.txt`

---

## Task 4: Storage Architecture for ML — Object Storage, Vector DBs & Data Lakes

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Object storage (S3/MinIO): storing datasets, models, and artifacts
- Vector databases: storing and searching embeddings
- Storage tiering: hot, warm, cold, archive
- Data lifecycle policies and cost optimisation

**What to read first:**
- 📖 [MinIO: Quickstart](https://min.io/docs/minio/linux/operations/installation.html) (S3‑compatible, local)
- 📖 [ChromaDB: Getting Started](https://docs.trychroma.com/getting-started) (open‑source vector DB)
- 📖 [Milvus: Introduction](https://milvus.io/docs/overview.md) (open‑source vector DB)
- 📖 [LanceDB: Getting Started](https://lancedb.github.io/lancedb/) (embedded vector DB)

**Task:**
1. Write `object_storage_client.py` using MinIO (or mock S3):
   - Upload a dataset (CSV → Parquet conversion before upload)
   - Upload a trained model (versioned: `models/v1/model.pkl`, `models/v2/model.pkl`)
   - Download and verify (checksum comparison)
   - List all objects with metadata (size, last modified, version)
   - Implement a simple lifecycle policy: "delete objects older than 30 days from the `temp/` prefix"
2. Write `vector_db_demo.py` using ChromaDB:
   - Create a collection
   - Generate embeddings for 1,000 text documents (use a sentence‑transformers model from Hugging Face)
   - Insert embeddings with metadata (category, date, source)
   - Query: "find 5 most similar documents to a given query"
   - Filter: "find similar documents, but only from category X"
   - Benchmark: query latency for 100, 1K, 10K, 100K documents
3. Write `storage_comparison.py`:
   - Compare storage options for different ML artifacts:
     - Raw data (CSV, 10GB) → object storage
     - Processed features (Parquet, 2GB) → object storage or data lake
     - Model files (500MB) → object storage + registry
     - Embeddings (1M vectors, 768 dimensions) → vector DB
     - Experiment logs → database or file system
   - Estimate storage costs for each at different scales
4. Write `storage_architecture.md`:
   - Diagram: data sources → object storage (bronze) → processed (silver) → features (gold) → vector DB + model registry
   - Decision matrix: when to use SQL vs object storage vs vector DB vs file system
   - Cost modelling: storage cost at 1TB, 10TB, 100TB (using public pricing)

**Deliverables:**
1. `/cloud_architect/task4/object_storage_client.py`
2. `/cloud_architect/task4/vector_db_demo.py`
3. `/cloud_architect/task4/storage_comparison.py`
4. `/cloud_architect/task4/storage_architecture.md` — diagrams + decision matrix
5. `/cloud_architect/task4/requirements.txt`

---

## Task 5: Compute Architecture — GPUs, Scaling & Cost Optimisation

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- GPU types and their ML workload suitability
- Scaling strategies: vertical vs horizontal, autoscaling
- Spot/preemptible instances: saving 70% on training costs
- Batch vs real‑time compute patterns
- Cost optimisation strategies for ML workloads

**What to read first:**
- 📖 [Tim Dettmers: Which GPU for Deep Learning?](https://timdettmers.com/2023/01/30/which-gpu-for-deep-learning/) (comprehensive guide)
- 📖 [Google Colab: GPU Runtime](https://colab.research.google.com/) (free GPU access)
- 📖 [Lambda Labs: GPU Benchmarks](https://lambdalabs.com/gpu-benchmarks) (comparison)
- 📖 [Kubernetes: Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) (autoscaling concepts)

**Task:**
1. Write `gpu_benchmark.py` (runs on CPU if no GPU — simulate with timing estimates):
   - Benchmark matrix multiplication at different sizes (1K×1K to 10K×10K): CPU vs GPU (if available)
   - Benchmark model inference: batch sizes 1, 8, 32, 64, 128 — measure latency and throughput
   - Profile memory usage during training (peak memory, gradient memory, activation memory)
   - Output: comparison table with speedup ratios
2. Write `cost_calculator.py`:
   - For a given ML workload, estimate costs across options:
     - **Training**: on‑demand GPU, spot GPU, Google Colab (free), local machine
     - **Serving**: serverless (per‑request), always‑on container, autoscaled containers
   - Inputs: model size, training hours, requests/day, SLA requirements
   - Output: monthly cost comparison table + recommendation
   - Include: "break‑even analysis" — when does a reserved instance become cheaper than on‑demand?
3. Write `autoscaling_simulator.py`:
   - Simulate request traffic over 24 hours (peak during business hours, low at night)
   - Model 3 scaling strategies:
     - Fixed capacity (always 10 replicas)
     - Reactive autoscaling (scale based on current CPU utilisation)
     - Predictive autoscaling (pre‑scale based on time‑of‑day patterns)
   - For each: compute total compute hours, average latency, cost
   - Plot: traffic vs replicas vs latency over 24 hours for each strategy
4. Write `compute_architecture.md`:
   - GPU selection guide: T4 vs A100 vs H100 (use cases, memory, cost/hour)
   - Training cost optimisation checklist (10 items: mixed precision, gradient accumulation, data loading, spot instances, etc.)
   - Serving cost optimisation: model distillation, quantisation, batching, caching, autoscaling
   - Decision tree: when to use GPU vs CPU for inference

**Deliverables:**
1. `/cloud_architect/task5/gpu_benchmark.py`
2. `/cloud_architect/task5/cost_calculator.py`
3. `/cloud_architect/task5/autoscaling_simulator.py`
4. `/cloud_architect/task5/compute_architecture.md` — GPU guide + cost optimisation
5. `/cloud_architect/task5/requirements.txt`

---

## Task 6: ML System Design — Patterns & Anti‑Patterns

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Common ML system architecture patterns
- Designing for reliability: redundancy, failover, graceful degradation
- Designing for latency: caching, precomputation, model optimisation
- Anti‑patterns: what NOT to do in ML systems

**What to read first:**
- 📖 [Chip Huyen: ML Systems Design (Free Outline)](https://huyenchip.com/machine-learning-systems-design/toc.html)
- 📖 [Google: ML Design Patterns (O'Reilly summary)](https://cloud.google.com/architecture/ml-design-patterns) (catalogue)
- 📖 [Uber: Michelangelo](https://www.uber.com/en-IN/blog/michelangelo-machine-learning-platform/) (real‑world platform)
- 📖 [Martin Kleppmann: Designing Data‑Intensive Applications (summary)](https://dataintensive.net/) (architecture principles)

**Task:**
1. Write system designs for 3 different ML use cases (each as a separate markdown section):
   - **Real‑time recommendation system** (e‑commerce product recommendations)
   - **Batch fraud detection pipeline** (daily processing of transactions)
   - **Search ranking with ML** (re‑ranking search results)
2. For each system design, include:
   - **Requirements**: functional (what it does) + non‑functional (latency SLA, throughput, availability)
   - **High‑Level Architecture**: Mermaid diagram showing components and data flow
   - **Data Flow**: how data moves from source → processing → model → serving → storage
   - **Model Serving Strategy**: online vs batch vs hybrid, with justification
   - **Caching Strategy**: what to cache, TTL, invalidation
   - **Failure Handling**: what happens when the model is down? (fallback to rules‑based, serve cached predictions, return default)
   - **Scaling Strategy**: what triggers scaling, how to scale each component
   - **Estimated Costs**: rough order of magnitude at given scale
3. Write `anti_patterns.md`:
   - 10 common ML system anti‑patterns with explanations:
     - Training/serving skew
     - Feature store bypass (computing features differently in training vs serving)
     - Monolithic model services
     - No model versioning
     - Ignoring data quality
     - Over‑engineering for scale you don't have
     - No fallback strategy
     - Coupling model updates to code deployments
     - Using the wrong metric to optimise
     - Not monitoring model performance in production

**Deliverables:**
1. `/cloud_architect/task6/recommendation_system_design.md`
2. `/cloud_architect/task6/fraud_detection_design.md`
3. `/cloud_architect/task6/search_ranking_design.md`
4. `/cloud_architect/task6/anti_patterns.md` — 10 anti‑patterns
5. `/cloud_architect/task6/design_template.md` — your reusable system design template

---

## Task 7: Observability Stack — Monitoring, Logging & Tracing for ML

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- The three pillars of observability: metrics, logs, traces
- Setting up Prometheus + Grafana for ML metrics
- Structured logging for ML services
- Distributed tracing for multi‑service ML pipelines
- Alert design: reducing noise, actionable alerts

**What to read first:**
- 📖 [Prometheus: Getting Started](https://prometheus.io/docs/prometheus/latest/getting_started/) (metrics)
- 📖 [Grafana: Getting Started](https://grafana.com/docs/grafana/latest/getting-started/) (dashboards)
- 📖 [OpenTelemetry: Python Instrumentation](https://opentelemetry.io/docs/languages/python/) (tracing)
- 📖 [Google SRE Book: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) (free, chapter 6)

**Task:**
1. Write `metrics_exporter.py`:
   - Instrument your ML API with Prometheus metrics:
     - `prediction_requests_total` (counter, labels: model_version, status_code)
     - `prediction_latency_seconds` (histogram, labels: model_version)
     - `model_prediction_value` (histogram — distribution of predictions)
     - `feature_value` (gauge — track individual feature distributions)
     - `model_loaded` (gauge — 1 if model loaded, 0 if not)
   - Expose metrics at `/metrics` endpoint
2. Write `docker-compose.monitoring.yml`:
   - ML API service (with metrics endpoint)
   - Prometheus (scraping the API metrics)
   - Grafana (with pre‑configured dashboards)
   - Provide `prometheus.yml` config and `grafana/dashboards/ml_dashboard.json`
3. Write `structured_logger.py`:
   - JSON‑structured logging with fields: timestamp, level, service, request_id, model_version, latency_ms, prediction, features_hash
   - Correlation ID: pass a request_id through all components
   - Log aggregation: write to both console and file with rotation
4. Write `alerting_rules.yml` (Prometheus format):
   - Alert: prediction latency P95 > 500ms for 5 minutes
   - Alert: error rate > 5% for 10 minutes
   - Alert: no predictions in 15 minutes (service might be down)
   - Alert: prediction distribution shift (mean prediction changed by > 2 std)
   - For each alert: severity, summary, description, runbook link
5. Write `observability_guide.md`:
   - The three pillars explained with ML‑specific examples
   - Dashboard design principles: 4 golden signals (latency, traffic, errors, saturation)
   - Alert fatigue: how to reduce false alarms
   - Observability maturity model for ML systems

**Deliverables:**
1. `/cloud_architect/task7/metrics_exporter.py`
2. `/cloud_architect/task7/docker-compose.monitoring.yml` + prometheus.yml + grafana dashboard
3. `/cloud_architect/task7/structured_logger.py`
4. `/cloud_architect/task7/alerting_rules.yml`
5. `/cloud_architect/task7/observability_guide.md`

---

## Task 8: Disaster Recovery, High Availability & SLOs for ML Systems

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- Service Level Objectives (SLOs), Service Level Indicators (SLIs), and Error Budgets
- High Availability patterns: redundancy, failover, health checks
- Disaster Recovery: RPO (Recovery Point Objective) and RTO (Recovery Time Objective)
- Chaos engineering concepts for ML systems
- Capacity planning

**What to read first:**
- 📖 [Google SRE Book: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) (free, chapter 4)
- 📖 [Google SRE Book: Embracing Risk](https://sre.google/sre-book/embracing-risk/) (free, chapter 3)
- 📖 [Principles of Chaos Engineering](https://principlesofchaos.org/) (manifesto)
- 📖 [AWS: Disaster Recovery Strategies](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html) (concepts apply everywhere)

**Task:**
1. Write `slo_definition.md`:
   - Define SLOs for an ML prediction service:
     - Availability: 99.9% (8.76 hours downtime/year)
     - Latency: P99 < 200ms
     - Accuracy: model accuracy > 85% (measured weekly)
     - Freshness: model retrained within 7 days of drift detection
   - Define SLIs for each SLO (what exactly do you measure?)
   - Calculate error budgets: 99.9% availability = 43.8 minutes downtime/month
   - Policy: what happens when error budget is exhausted? (freeze deployments)
2. Write `ha_simulator.py`:
   - Simulate an ML service with 3 replicas behind a load balancer
   - Simulate failures: one replica crashes, slow replica, model loading failure
   - Implement health checks: the load balancer detects unhealthy replicas
   - Implement circuit breaker: if model fails 5x in a row → fallback to cached predictions
   - Measure: availability % during different failure scenarios
3. Write `dr_plan.md`:
   - **What to back up**: model files, training data references, config, feature definitions
   - **RPO**: how much data loss is acceptable? (last model version = hours/days)
   - **RTO**: how quickly must we recover? (minutes for serving, hours for training)
   - **Recovery procedures**:
     - Model serving failure → roll back to previous model version (steps)
     - Data corruption → restore from backup (steps)
     - Complete infrastructure failure → rebuild from Terraform + model registry (steps)
   - **DR test plan**: quarterly drill checklist
4. Write `capacity_planner.py`:
   - Given: current traffic, growth rate, model latency, acceptable P99 latency
   - Calculate: required replicas now, in 3 months, in 6 months, in 1 year
   - Factor in: peak vs average traffic (peak = 3x average)
   - Output: capacity planning table + cost projection

**Deliverables:**
1. `/cloud_architect/task8/slo_definition.md` — SLOs, SLIs, error budgets
2. `/cloud_architect/task8/ha_simulator.py`
3. `/cloud_architect/task8/dr_plan.md` — disaster recovery plan
4. `/cloud_architect/task8/capacity_planner.py`
5. `/cloud_architect/task8/requirements.txt`

---

## Task 9: Multi‑Environment Architecture — Dev, Staging, Production

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Environment management: dev, staging, production — why and how
- Environment parity: keeping environments consistent
- Configuration management across environments
- Promotion workflows: code and models moving through environments
- Cost management: dev shouldn't cost as much as prod

**What to read first:**
- 📖 [12‑Factor App](https://12factor.net/) (all 12 factors — essential reading)
- 📖 [GitOps: What is it?](https://www.gitops.tech/) (declarative infrastructure)
- 📖 [Argo CD: Getting Started](https://argo-cd.readthedocs.io/en/stable/getting-started/) (GitOps for K8s)
- 📖 [Terraform Workspaces](https://developer.hashicorp.com/terraform/language/state/workspaces) (multi‑environment IaC)

**Task:**
1. Write `environment_configs/`:
   - `dev/config.yaml`: small model, debug logging, mock data, single replica, local storage
   - `staging/config.yaml`: full model, info logging, production data subset, 2 replicas, MinIO storage
   - `prod/config.yaml`: full model, warn logging, production data, 3+ replicas, MinIO storage, auth required
2. Write `environment_manager.py`:
   - A CLI tool that:
     - `python env_manager.py create dev` — spins up dev environment (Docker Compose)
     - `python env_manager.py create staging` — spins up staging (more services, more resources)
     - `python env_manager.py promote dev staging` — promotes config/model from dev to staging
     - `python env_manager.py promote staging prod` — promotes from staging to prod (with validation gate)
     - `python env_manager.py destroy dev` — tears down an environment
3. Write `promotion_pipeline.py`:
   - Automate the promotion workflow:
     - Dev → Staging: run integration tests, if pass → promote
     - Staging → Prod: run load tests + model validation + security scan, if all pass → promote
   - Gate checks: model accuracy > threshold, latency < threshold, no security vulnerabilities
   - Rollback: if production deployment fails health checks → auto‑rollback to previous version
4. Write `docker-compose.dev.yml` and `docker-compose.staging.yml`:
   - Dev: API (1 replica) + DuckDB
   - Staging: API (2 replicas) + MinIO + MLflow + monitoring stack
5. Write `environment_guide.md`:
   - When to use each environment
   - What should be the same across environments? (code, model code) What can differ? (resources, replicas, data size)
   - Cost optimisation: dev environment auto‑shutdown schedule
   - Promotion checklist template

**Deliverables:**
1. `/cloud_architect/task9/environment_configs/` — dev, staging, prod config files
2. `/cloud_architect/task9/environment_manager.py`
3. `/cloud_architect/task9/promotion_pipeline.py`
4. `/cloud_architect/task9/docker-compose.dev.yml` + `docker-compose.staging.yml`
5. `/cloud_architect/task9/environment_guide.md` — environments + promotion workflow

---

## Task 10: Architecture Review — Design a Complete ML Platform from Scratch

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- End‑to‑end ML platform architecture design
- Technology selection: making defensible choices
- Architecture Decision Records (ADRs)
- Cost estimation at scale
- Presenting architecture to stakeholders

**What to read first:**
- 📖 [Google: MLOps — Continuous Delivery for ML](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning) (reference architecture)
- 📖 [Architecture Decision Records](https://adr.github.io/) (ADR format)
- 📖 [C4 Model: Visualising Software Architecture](https://c4model.com/) (diagramming standard)
- 📖 [The Architecture of Open Source Applications](https://aosabook.org/en/) (learning from real systems)

**Task:**
1. **Scenario**: A mid‑size company (100 employees, 5 data scientists, 2 ML engineers) wants to build an ML platform that supports:
   - 3 ML use cases: customer churn prediction, product recommendation, demand forecasting
   - Data: 500GB growing 10GB/month, from PostgreSQL + event streams + CSV uploads
   - Serving: 10K predictions/day (churn), 1M predictions/day (recommendations), weekly batch (forecasting)
   - Team: data scientists should be able to deploy models with minimal DevOps help
   - Budget: $5,000/month for infrastructure (using free tools where possible)
2. Write `platform_design.md` (the main deliverable — 8+ pages):
   - **C4 Context Diagram**: system in its environment (users, external systems)
   - **C4 Container Diagram**: major components and their interactions
   - **C4 Component Diagram**: internal structure of the serving layer
   - **Technology Choices**: for each component, justify your choice (table: component, chosen tech, alternatives considered, why chosen)
   - **Data Architecture**: source → ingestion → storage → processing → features → model → serving
   - **Deployment Architecture**: environments, CI/CD pipeline, promotion workflow
   - **Security Architecture**: authentication, authorisation, encryption, audit logging
   - **Cost Estimate**: detailed monthly cost breakdown by component
   - **Scaling Plan**: what to do when traffic 10x or data 10x
   - **Risk Register**: 5 risks with likelihood, impact, and mitigation
3. Write 3 Architecture Decision Records (ADRs):
   - `adr/001-object-storage.md`: Why MinIO over direct filesystem
   - `adr/002-serving-framework.md`: Why FastAPI + Docker over managed ML serving
   - `adr/003-orchestration.md`: Why Airflow over Prefect (or vice versa)
   - Each ADR: Title, Status, Context, Decision, Consequences
4. Write `stakeholder_presentation.md`:
   - A 10‑slide outline for presenting the architecture to non‑technical leadership:
     - Slide 1: What problem are we solving?
     - Slide 2: Current state (manual, slow, unreliable)
     - Slide 3: Proposed architecture (one simple diagram)
     - Slide 4–6: Key capabilities enabled
     - Slide 7: Cost and timeline
     - Slide 8: Risks and mitigations
     - Slide 9: What the team needs (headcount, training)
     - Slide 10: Recommended next steps

**Deliverables:**
1. `/cloud_architect/task10/platform_design.md` — full architecture document
2. `/cloud_architect/task10/adr/` — 3 Architecture Decision Records
3. `/cloud_architect/task10/stakeholder_presentation.md` — 10‑slide outline
4. `/cloud_architect/task10/cost_breakdown.csv` — detailed cost estimate
5. `/cloud_architect/task10/architecture_diagrams/` — C4 diagrams in Mermaid format

---

## Learning Path Summary

| Task | Topic | Difficulty | Key Tools |
|------|-------|-----------|-----------|
| 1 | Cloud Fundamentals & AI/ML Service Map | ⭐ | Markdown, Python |
| 2 | Infrastructure as Code (Terraform) | ⭐⭐ | Terraform, Docker |
| 3 | Networking & Security for ML | ⭐⭐ | FastAPI, JWT, Vault |
| 4 | Storage Architecture (Object + Vector) | ⭐⭐⭐ | MinIO, ChromaDB |
| 5 | Compute Architecture & Cost Optimisation | ⭐⭐⭐ | Python, benchmarking |
| 6 | ML System Design Patterns | ⭐⭐⭐ | Mermaid, Markdown |
| 7 | Observability Stack (Prometheus + Grafana) | ⭐⭐⭐⭐ | Prometheus, Grafana, Docker |
| 8 | DR, HA & SLOs for ML Systems | ⭐⭐⭐⭐ | Python, SRE concepts |
| 9 | Multi‑Environment Architecture | ⭐⭐⭐⭐⭐ | Docker Compose, Python CLI |
| 10 | Full ML Platform Architecture Design | ⭐⭐⭐⭐⭐ | C4 Model, ADRs, Mermaid |

**All tools are free and open‑source. No paid cloud services required.**
