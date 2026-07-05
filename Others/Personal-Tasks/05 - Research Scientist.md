# Research Scientist / Applied Scientist — 10 Tasks (Beginner → 2‑Year Experience)

> **Goal:** Go from "I know Python and basic ML" to "I can read papers, reproduce results, design experiments, and push the state of the art."
> A Research/Applied Scientist combines deep theoretical knowledge with rigorous experimentation — you formulate hypotheses, implement novel methods, and publish findings.
> Each task is self‑contained. Difficulty increases from Task 1 → 10.

---

## Task 1: Read, Understand & Summarise a Research Paper

**Difficulty:** ⭐ Beginner

**What you'll learn:**
- How to read an ML research paper efficiently (3‑pass method)
- Understanding paper structure: abstract, intro, related work, method, experiments, ablation, conclusion
- Extracting key contributions vs incremental improvements
- Building a paper reading habit

**What to read first:**
- 📖 [How to Read a Paper — S. Keshav (3‑pass approach)](http://ccr.sigcomm.org/online/files/p83-keshavA.pdf) (3 pages, essential)
- 📖 [Yannic Kilcher: How I Read Papers](https://www.youtube.com/watch?v=SHTOI0KtZnU) (15 min)
- 📖 [Papers with Code](https://paperswithcode.com/) — papers with linked implementations
- 📖 [Arxiv Sanity Preserver](http://arxiv-sanity-lite.com/) — find relevant papers

**Task:**
1. Pick 3 foundational papers (one from each era):
   - Classic: ["Random Forests" — Breiman (2001)](https://link.springer.com/article/10.1023/A:1010933404324)
   - Deep Learning: ["Attention Is All You Need" — Vaswani et al. (2017)](https://arxiv.org/abs/1706.03762)
   - Recent: Pick any paper from the last 12 months on [Papers with Code](https://paperswithcode.com/) with a trending badge
2. For each paper, write a structured summary in `paper_summaries.md`:
   - **Problem**: What problem does the paper solve? (2 sentences)
   - **Key Contribution**: What is new? (2 sentences)
   - **Method**: How does it work? (1 paragraph, no math — explain to a smart colleague)
   - **Results**: What did they achieve? (key numbers + baseline comparison)
   - **Limitations**: What didn't they solve or test?
   - **Your Questions**: 3 questions you'd ask the authors
3. Create a `paper_comparison_table.md` — table comparing the 3 papers on: year, problem type, dataset used, key metric, reproducibility (code available?), citation count.

**Deliverables:**
1. `/research_scientist/task1/paper_summaries.md` — 3 structured summaries
2. `/research_scientist/task1/paper_comparison_table.md`
3. `/research_scientist/task1/reading_template.md` — your reusable template for future papers

---

## Task 2: Reproduce a Published Result from Scratch

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- Setting up a reproducible experiment environment
- Implementing a method from a paper description (not just cloning a repo)
- Matching published results (or understanding why they differ)
- The gap between paper descriptions and actual implementation

**What to read first:**
- 📖 [Reproducibility in ML — NeurIPS Checklist](https://neurips.cc/Conferences/2024/PaperInformation/PaperChecklist) (what reviewers look for)
- 📖 [Papers with Code: Reproducibility Reports](https://paperswithcode.com/rc2022) (community reproductions)
- 📖 [PyTorch: 60‑Minute Blitz](https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html) (if needed)

**Task:**
1. Pick a reproducible paper with known results: [ResNet on CIFAR‑10](https://arxiv.org/abs/1512.03385) or [Word2Vec Skip‑Gram](https://arxiv.org/abs/1301.3781) or any paper from [Papers with Code](https://paperswithcode.com/) with code and a leaderboard.
2. **Do NOT clone the authors' repo.** Implement the core method yourself from the paper description.
3. Write `reproduce.py` that:
   - Implements the model architecture as described in the paper
   - Uses the same dataset (or a subset for compute reasons — document this)
   - Uses the same hyperparameters mentioned in the paper
   - Trains the model, logs metrics per epoch
   - Reports the final metric and compares to the published result
4. Write `reproduction_report.md`:
   - Your result vs published result (table)
   - What was ambiguous in the paper? What did you have to guess?
   - What implementation details mattered most for matching the result?
   - If your result differs, hypothesise why (compute, data, undocumented tricks)
5. Document your environment: `environment.yaml` or `requirements.txt` with exact versions.

**Deliverables:**
1. `/research_scientist/task2/reproduce.py` — your implementation
2. `/research_scientist/task2/reproduction_report.md`
3. `/research_scientist/task2/training_log.csv` — epoch, loss, metric per epoch
4. `/research_scientist/task2/requirements.txt` — pinned dependencies
5. `/research_scientist/task2/plots/` — training curves (loss, accuracy vs epoch)

---

## Task 3: Mathematical Foundations — Implement Core Algorithms from Scratch

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- Gradient descent: batch, stochastic, mini‑batch
- Backpropagation: the chain rule in action
- Loss functions: MSE, cross‑entropy, hinge loss
- Regularisation: L1, L2, dropout (conceptual)
- NumPy‑only implementations (no frameworks)

**What to read first:**
- 📖 [3Blue1Brown: Neural Networks (full playlist)](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi) (4 videos, ~1 hour)
- 📖 [Stanford CS231n: Backpropagation](https://cs231n.github.io/optimization-2/) (notes)
- 📖 [Matrix Calculus for Deep Learning — Explained.ai](https://explained.ai/matrix-calculus/) (reference)
- 📖 [Andrew Ng: Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction) (free to audit, weeks 1–3)

**Task:**
1. Write `linear_regression_scratch.py` using only NumPy:
   - Implement gradient descent for linear regression (MSE loss)
   - Train on a synthetic dataset (y = 3x₁ + 2x₂ + 1 + noise)
   - Plot loss vs iteration → confirm convergence
   - Compare your weights to sklearn's `LinearRegression` — they should match
2. Write `logistic_regression_scratch.py` using only NumPy:
   - Implement binary cross‑entropy loss + sigmoid
   - Implement gradient descent with learning rate schedule
   - Train on a 2D synthetic classification dataset
   - Plot the decision boundary
   - Compare accuracy to sklearn's `LogisticRegression`
3. Write `neural_net_scratch.py` using only NumPy:
   - Implement a 2‑layer neural network (input → hidden → output)
   - Forward pass + backward pass (backpropagation by hand)
   - Train on XOR problem or a simple 2D dataset
   - Plot loss curve and decision boundary
4. Write `math_foundations_report.md`:
   - Derive the gradient update rule for logistic regression (show the math)
   - Explain backpropagation in your own words (chain rule applied)
   - What happens when learning rate is too high? Too low? Show plots.

**Deliverables:**
1. `/research_scientist/task3/linear_regression_scratch.py`
2. `/research_scientist/task3/logistic_regression_scratch.py`
3. `/research_scientist/task3/neural_net_scratch.py`
4. `/research_scientist/task3/math_foundations_report.md` — derivations + explanations
5. `/research_scientist/task3/plots/` — convergence, decision boundaries, learning rate experiments

---

## Task 4: Experimental Design — Ablation Studies & Statistical Rigour

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Designing controlled experiments: one variable at a time
- Ablation studies: quantifying the contribution of each component
- Statistical significance in ML experiments: confidence intervals, multiple comparisons
- Random seeds and variance: how to report results honestly
- Proper baselines and fair comparisons

**What to read first:**
- 📖 [Dodge et al.: Show Your Work — Improved Reporting of Experimental Results](https://arxiv.org/abs/1909.03004) (8 pages)
- 📖 [Bouthillier et al.: Accounting for Variance in ML Benchmarks](https://arxiv.org/abs/2103.03098)
- 📖 [Google: ML Testing Rubric](https://developers.google.com/machine-learning/testing-debugging) (best practices)

**Task:**
1. Pick a model (e.g., a CNN on CIFAR‑10 or a text classifier on a sentiment dataset).
2. Write `ablation_study.py` that runs a systematic ablation:
   - **Full model**: all components enabled (your best config)
   - **Remove component A**: e.g., remove data augmentation → measure impact
   - **Remove component B**: e.g., remove learning rate scheduling → measure impact
   - **Remove component C**: e.g., remove dropout → measure impact
   - **Remove component D**: e.g., reduce model size by 50% → measure impact
   - Each experiment runs with **5 different random seeds** → report mean ± std
3. Write `seed_variance.py`:
   - Train the same model with 10 different seeds
   - Plot the distribution of final accuracies
   - Compute the 95% confidence interval
   - Discuss: is the variance small enough to trust a single‑run result?
4. Write `ablation_report.md`:
   - Ablation table: component removed → accuracy change (mean ± std)
   - Rank components by importance
   - Statistical test: is the difference between full model and ablated version significant? (paired t‑test)
   - Your protocol: how many seeds should you run? When can you skip ablations?

**Deliverables:**
1. `/research_scientist/task4/ablation_study.py`
2. `/research_scientist/task4/seed_variance.py`
3. `/research_scientist/task4/ablation_report.md`
4. `/research_scientist/task4/plots/` — ablation bar chart with error bars, seed distribution
5. `/research_scientist/task4/experiment_log.csv` — every run: seed, config, metric

---

## Task 5: Literature Review & Research Gap Identification

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Conducting a structured literature review
- Identifying research gaps and open problems
- Organising related work into a taxonomy
- Writing a related work section that tells a coherent story

**What to read first:**
- 📖 [Semantic Scholar](https://www.semanticscholar.org/) — AI‑powered paper search
- 📖 [Connected Papers](https://www.connectedpapers.com/) — visual graph of related papers
- 📖 [How to Write a Good Related Work Section — Knuth](https://www.cs.cmu.edu/~jrs/sins.html) (classic advice)
- 📖 [Google Scholar](https://scholar.google.com/) — citation tracking

**Task:**
1. Pick a specific research topic (narrow scope): e.g., "Parameter‑efficient fine‑tuning of LLMs" or "Data augmentation for small medical image datasets" or "Contrastive learning for NLP."
2. Find 15–20 relevant papers using Semantic Scholar, Google Scholar, and Connected Papers.
3. Write `literature_review.md`:
   - **Taxonomy**: Organise papers into 3–4 categories (e.g., for PEFT: adapter methods, prompt tuning, LoRA variants, pruning approaches)
   - **Timeline**: evolution of the field (key milestones)
   - **Comparison table**: paper, method, dataset, key metric, strengths, limitations
   - **Research gaps**: 3 specific gaps you identified (not vague — e.g., "No paper has tested LoRA on encoder‑only models for token classification")
   - **Proposed direction**: for each gap, sketch a 1‑paragraph research idea
4. Create `paper_graph.md` — a Mermaid diagram showing how the 15 papers relate (who cites whom, which ideas build on which).

**Deliverables:**
1. `/research_scientist/task5/literature_review.md` — taxonomy + comparison + gaps
2. `/research_scientist/task5/paper_graph.md` — Mermaid citation/concept graph
3. `/research_scientist/task5/papers.bib` — BibTeX entries for all 15–20 papers
4. `/research_scientist/task5/reading_notes/` — individual notes per paper (1 page each)

---

## Task 6: Implement a Novel Loss Function & Benchmark It

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Understanding loss functions deeply: gradients, landscape, convergence properties
- Implementing custom loss functions in PyTorch
- Fair benchmarking: same data, same model, same hyperparameters, different loss
- Visualising loss landscapes

**What to read first:**
- 📖 [Li et al.: Visualizing the Loss Landscape of Neural Nets](https://arxiv.org/abs/1712.09913) (NeurIPS 2018)
- 📖 [PyTorch: Custom Loss Functions](https://pytorch.org/docs/stable/nn.html#loss-functions) (docs)
- 📖 [Focal Loss — Lin et al.](https://arxiv.org/abs/1708.02002) (ICCV 2017 — for imbalanced data)
- 📖 [Label Smoothing — Müller et al.](https://arxiv.org/abs/1906.02629)

**Task:**
1. Pick a classification task with class imbalance: [Kaggle Credit Card Fraud](https://www.kaggle.com/mlg-ulb/creditcardfraud) or create a synthetic imbalanced dataset (95:5 ratio).
2. Write `custom_losses.py` implementing these loss functions in PyTorch:
   - Standard Cross‑Entropy
   - Weighted Cross‑Entropy (class weights proportional to inverse frequency)
   - Focal Loss (with configurable γ — test γ = 0, 1, 2, 5)
   - Label Smoothing Cross‑Entropy (with smoothing = 0.1)
3. Write `benchmark_losses.py` that:
   - Trains the **same model** (e.g., a 3‑layer MLP) with each loss function
   - Uses the same data split, same optimiser, same LR, same epochs
   - Logs per‑epoch: train loss, val loss, val accuracy, val F1, val precision, val recall
   - Runs each configuration with 3 seeds → report mean ± std
4. Write `loss_analysis.md`:
   - Table: loss function → final F1 (mean ± std), precision, recall
   - Which loss worked best for the minority class? Why?
   - Plot: training curves for all 4 losses on the same chart
   - When to use each loss function (decision guide)

**Deliverables:**
1. `/research_scientist/task6/custom_losses.py` — 4 loss implementations
2. `/research_scientist/task6/benchmark_losses.py`
3. `/research_scientist/task6/loss_analysis.md`
4. `/research_scientist/task6/plots/` — training curves, F1 comparison, focal loss γ sensitivity
5. `/research_scientist/task6/requirements.txt`

---

## Task 7: Advanced Optimisation — Beyond SGD

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- Optimiser landscape: SGD, Momentum, Adam, AdamW, LAMB, SAM
- Learning rate schedules: step decay, cosine annealing, warm‑up, cyclical LR
- Gradient clipping and its effect on training stability
- Implementing a custom optimiser in PyTorch

**What to read first:**
- 📖 [Sebastian Ruder: An Overview of Gradient Descent Optimization Algorithms](https://ruder.io/optimizing-gradient-descent/) (comprehensive blog post)
- 📖 [Loshchilov & Hutter: Decoupled Weight Decay Regularization (AdamW)](https://arxiv.org/abs/1711.05101)
- 📖 [Foret et al.: Sharpness‑Aware Minimization (SAM)](https://arxiv.org/abs/2010.01412) (ICLR 2021)
- 📖 [PyTorch: Learning Rate Schedulers](https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate)

**Task:**
1. Write `optimiser_comparison.py` that:
   - Trains a CNN on CIFAR‑10 (or Fashion‑MNIST for speed) using 5 optimisers:
     - SGD (with momentum 0.9)
     - Adam (default β1=0.9, β2=0.999)
     - AdamW (weight decay = 0.01)
     - SGD + Cosine Annealing LR
     - Adam + Linear Warm‑up (warm up for 5% of steps) + Cosine Decay
   - All use the same model, same data, same number of epochs
   - Logs: train loss, val loss, val accuracy per epoch
   - Plots all 5 training curves on one chart + all 5 val accuracy curves on another
2. Write `lr_schedule_viz.py`:
   - Plot 5 LR schedules over 100 epochs: constant, step decay, cosine annealing, warm‑up + cosine, cyclical
   - Show how each schedule affects the learning rate over time
3. Write `custom_optimiser.py`:
   - Implement SAM (Sharpness‑Aware Minimisation) from scratch in PyTorch
   - Train the same CNN with SAM vs Adam → compare final accuracy
4. Write `optimiser_report.md`:
   - Comparison table: optimiser, final val accuracy, convergence speed (epoch where val acc > 85%)
   - Which optimiser converges fastest? Which achieves best final accuracy?
   - Rule of thumb: which optimiser to start with for different tasks

**Deliverables:**
1. `/research_scientist/task7/optimiser_comparison.py`
2. `/research_scientist/task7/lr_schedule_viz.py`
3. `/research_scientist/task7/custom_optimiser.py` — SAM implementation
4. `/research_scientist/task7/optimiser_report.md`
5. `/research_scientist/task7/plots/` — training curves, LR schedules, SAM vs Adam

---

## Task 8: Scaling Experiments — Multi‑GPU, Mixed Precision & Efficient Training

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- Mixed precision training (FP16/BF16) and why it speeds up training
- Gradient accumulation for simulating large batches
- Data‑parallel training concepts (DDP)
- Profiling and identifying training bottlenecks
- Efficient data loading pipelines

**What to read first:**
- 📖 [PyTorch: Automatic Mixed Precision](https://pytorch.org/docs/stable/amp.html) (docs)
- 📖 [PyTorch: DistributedDataParallel](https://pytorch.org/tutorials/intermediate/ddp_tutorial.html) (tutorial)
- 📖 [Hugging Face: Efficient Training on a Single GPU](https://huggingface.co/docs/transformers/perf_train_gpu_one) (practical tips)
- 📖 [PyTorch Profiler](https://pytorch.org/tutorials/recipes/recipes/profiler_recipe.html)

**Task:**
1. Write `baseline_training.py`:
   - Train a model (ResNet‑18 on CIFAR‑10 or a transformer on a text dataset) in standard FP32
   - Log: time per epoch, peak GPU memory (or CPU memory if no GPU), throughput (samples/sec)
2. Write `mixed_precision.py`:
   - Add `torch.cuda.amp` (GradScaler + autocast) to the same training loop
   - Compare: time per epoch, memory, throughput vs FP32 baseline
   - If no GPU: simulate by comparing float32 vs float16 tensor operations and benchmarking
3. Write `gradient_accumulation.py`:
   - Implement gradient accumulation: effective batch size = 256, but actual batch = 32, accumulate over 8 steps
   - Compare training curve to actual batch_size=256 (if memory allows) and batch_size=32
   - Show that gradient accumulation ≈ large batch training
4. Write `profiling.py`:
   - Use `torch.profiler` (or `cProfile` + `line_profiler` for CPU) to identify the slowest parts of training
   - Profile: data loading, forward pass, backward pass, optimiser step
   - Identify the bottleneck and propose a fix (e.g., increase `num_workers`, use `pin_memory`)
5. Write `scaling_report.md`:
   - Table: technique, time_per_epoch, memory, accuracy (unchanged?), throughput
   - Profiling results: where is the bottleneck?
   - Checklist: "Before requesting more GPUs, try these 5 things first"

**Deliverables:**
1. `/research_scientist/task8/baseline_training.py`
2. `/research_scientist/task8/mixed_precision.py`
3. `/research_scientist/task8/gradient_accumulation.py`
4. `/research_scientist/task8/profiling.py`
5. `/research_scientist/task8/scaling_report.md`

---

## Task 9: Write a Research Paper — Full Manuscript in LaTeX

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Structuring a research paper: abstract, introduction, related work, methodology, experiments, conclusion
- Writing clearly and concisely for a technical audience
- Creating publication‑quality figures and tables
- LaTeX formatting and best practices
- The peer review process

**What to read first:**
- 📖 [Simon Peyton Jones: How to Write a Great Research Paper](https://www.microsoft.com/en-us/research/academic-program/write-great-research-paper/) (video, 30 min — essential)
- 📖 [Overleaf: LaTeX Tutorial (30 min)](https://www.overleaf.com/learn/latex/Learn_LaTeX_in_30_minutes)
- 📖 [NeurIPS Paper Template](https://neurips.cc/Conferences/2024/PaperInformation/StyleFiles) (standard format)
- 📖 [Tips for Writing NeurIPS Papers — Henning Schulzrinne](https://www.cs.columbia.edu/~hgs/etc/writing-tips.html)

**Task:**
1. Take one of your earlier experiments (e.g., loss function benchmark from Task 6 or optimiser comparison from Task 7) and frame it as a mini‑research paper.
2. Write the paper in LaTeX (or Markdown if LaTeX is too much):
   - **Abstract** (150 words): problem, method, key result
   - **Introduction** (1 page): motivation, gap, contribution statement
   - **Related Work** (0.5 page): position your work vs 5–8 related papers
   - **Method** (1 page): describe your approach formally (equations + algorithm pseudocode)
   - **Experiments** (1.5 pages): setup, datasets, baselines, results table, ablation table
   - **Analysis & Discussion** (0.5 page): what worked, what didn't, why
   - **Conclusion** (0.5 page): summary + future work (3 concrete directions)
   - **References**: proper BibTeX formatting
3. Create 3 publication‑quality figures:
   - A methods diagram (architecture or pipeline overview)
   - A results comparison chart (bar chart with error bars)
   - A training curve or analysis plot
4. Conduct a self‑review using the [NeurIPS Reviewer Checklist](https://neurips.cc/Conferences/2024/PaperInformation/PaperChecklist). Score your own paper.

**Deliverables:**
1. `/research_scientist/task9/paper.tex` (or `paper.md`) — full manuscript
2. `/research_scientist/task9/figures/` — 3+ publication‑quality figures
3. `/research_scientist/task9/references.bib` — BibTeX file
4. `/research_scientist/task9/self_review.md` — your self‑review against the checklist
5. `/research_scientist/task9/paper.pdf` — compiled PDF (if LaTeX)

---

## Task 10: Propose, Design & Run a Novel Experiment

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Formulating a research question from a gap in the literature
- Designing a rigorous experiment with proper controls
- Running, analysing, and interpreting results
- Negative results: what to do when your hypothesis is wrong
- The full research cycle: question → hypothesis → experiment → analysis → conclusion

**What to read first:**
- 📖 [Richard Hamming: You and Your Research](https://www.cs.virginia.edu/~robins/YouAndYourResearch.html) (legendary talk)
- 📖 [John Schulman: An Opinionated Guide to ML Research](http://joschu.net/blog/opinionated-guide-ml.html)
- 📖 [Karpathy: A Recipe for Training Neural Networks](http://karpathy.github.io/2019/04/25/recipe/) (practical wisdom)

**Task:**
1. Identify a research question from your Task 5 literature review (or pick a new one). Examples:
   - "Does label smoothing improve calibration on small datasets?"
   - "Can data augmentation replace 50% of the training data without accuracy loss?"
   - "Does warm‑up matter for Adam when training for < 10 epochs?"
2. Write `experiment_proposal.md`:
   - **Research Question**: clear, specific, testable
   - **Hypothesis**: what do you expect to find? Why?
   - **Variables**: independent (what you change), dependent (what you measure), controlled (what you keep constant)
   - **Baselines**: what will you compare against?
   - **Datasets**: at least 2 datasets to test generality
   - **Evaluation protocol**: metrics, number of seeds, statistical test
   - **Compute budget**: estimated time and resources
3. Write `run_experiment.py` that:
   - Implements the full experiment pipeline
   - Runs all conditions with multiple seeds
   - Logs all results to CSV
   - Handles failures gracefully (checkpoint, resume)
4. Write `experiment_results.md`:
   - Results table with confidence intervals
   - Was your hypothesis supported? Partially? Refuted?
   - What did you learn that was unexpected?
   - 3 follow‑up experiments that could extend this work
   - If negative result: explain why it's still valuable

**Deliverables:**
1. `/research_scientist/task10/experiment_proposal.md`
2. `/research_scientist/task10/run_experiment.py`
3. `/research_scientist/task10/experiment_results.md`
4. `/research_scientist/task10/results/` — CSVs + plots
5. `/research_scientist/task10/experiment_checklist.md` — your reusable checklist for future experiments

---

## Learning Path Summary

| Task | Topic | Difficulty | Key Tools |
|------|-------|-----------|-----------|
| 1 | Paper Reading & Summarisation | ⭐ | Semantic Scholar, Papers with Code |
| 2 | Reproducing Published Results | ⭐⭐ | PyTorch, NumPy |
| 3 | Math Foundations (From‑Scratch Implementations) | ⭐⭐ | NumPy only |
| 4 | Ablation Studies & Statistical Rigour | ⭐⭐⭐ | PyTorch, SciPy |
| 5 | Literature Review & Gap Identification | ⭐⭐⭐ | Semantic Scholar, Connected Papers |
| 6 | Custom Loss Functions & Benchmarking | ⭐⭐⭐ | PyTorch |
| 7 | Advanced Optimisation (SGD → SAM) | ⭐⭐⭐⭐ | PyTorch |
| 8 | Scaling: Mixed Precision, Grad Accumulation & Profiling | ⭐⭐⭐⭐ | PyTorch, torch.profiler |
| 9 | Writing a Research Paper (LaTeX) | ⭐⭐⭐⭐⭐ | LaTeX/Overleaf |
| 10 | Propose & Run a Novel Experiment | ⭐⭐⭐⭐⭐ | Full stack |

**All tools are free and open‑source. No paid cloud services required.**
