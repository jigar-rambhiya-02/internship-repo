# Agent Instructions: Role-Specific Learning Path Generator

When asked to generate the remaining role-specific learning paths, please strictly follow these guidelines:

## Task Structure & Difficulty
- **10 Tasks per Role**: Create exactly 10 tasks for each role.
- **Difficulty Curve**: Start at a **Beginner** level (for someone who knows basic Python) and progressively increase the difficulty up to a **2-year experience** level (Mid-level/Advanced) by Task 10.
- **Independent but Progressive**: Each task must be fully self-contained and independent (so AI can assist with one task without needing the code from the previous ones), but they should be logically ordered from easy to hard.

## Content & Format
- **Reading First**: Every task must include a "What to read first" section with links to relevant documentation, free courses, or videos (so the user can learn the theory before building).
- **Free/Open-Source Tools Only**: Strictly use free tools and open-source models (e.g., Hugging Face, Groq, Ollama, Scikit-learn, FastAPI). **Do not** require paid cloud services (no AWS/GCP lock-in) or paid APIs.
- **Generic & Industry-Agnostic**: Scenarios and datasets should be generic and widely applicable (e.g., e-commerce, generic HR, generic finance). Do not reference specific company names or proprietary client scenarios.
- **Minimize Overlap**: Intelligently reduce or merge tasks where roles share fundamental skills. Ensure each file focuses heavily on what is *unique* to that specific role.

## Expected Roles to Generate
(Check which ones have already been created and generate the missing ones):
1. Machine Learning Engineer (Created)
2. AI Engineer (Created)
3. Generative AI Engineer / Specialist (Created)
4. Data Scientist (Created)
5. Research Scientist / Applied Scientist (Created)
6. Data Engineer (Created)
7. MLOps Engineer (Created)
8. Cloud Solutions Architect (AI/ML focus) (Created)

## Output Format Example
For each task, use the following markdown structure:
```markdown
## Task [X]: [Task Title]

**Difficulty:** [⭐ to ⭐⭐⭐⭐⭐]

**What you'll learn:**
- [Bullet points of concepts]

**What to read first:**
- 📖 [Link Title](URL) - (Brief description)

**Task:**
1. [Step-by-step instructions...]

**Deliverables:**
1. `/role_name/taskX/file.py`
2. `/role_name/taskX/report.md`
```
