# Wohlig Prompt Template

A reliable, 6-section structure for production-grade AI prompts.
Fill every section for maximum consistency and accuracy.

---

## SECTION 1 — ROLE
> **What to put here:** Define who the model is acting as. Give it a job title, domain expertise, and optionally a persona or communication style. This primes the model's "voice" and knowledge scope.

```
You are a [job title / expert] with deep expertise in [domain].
You [communication style or key trait, e.g., "communicate in plain English" / "write with precision and no filler"].
```

---

## SECTION 2 — CONTEXT
> **What to put here:** Background information the model needs to do the task correctly. Include who the end-user is, what system/product this is part of, any domain-specific rules, or prior state the model should be aware of.

```
Background:
- [Who is the audience / end-user?]
- [What system, product, or workflow is this part of?]
- [Any domain rules, regulations, or constraints relevant to the task?]
- [Tone or brand guidelines if applicable]
```

---

## SECTION 3 — TASK
> **What to put here:** The actual instruction. Be explicit about the verb (summarize, classify, rewrite, extract, generate). One clear primary action. If there are sub-steps, list them in order.

```
Your task is to [primary action verb] the [input type] provided below.

Steps:
1. [Step 1]
2. [Step 2]
3. [Step 3 — if applicable]
```

---

## SECTION 4 — CONSTRAINTS
> **What to put here:** Hard rules the model must follow. Length limits, things to avoid, tone restrictions, what NOT to include, edge case handling. Think of these as guardrails.

```
Constraints:
- [Length limit, e.g., "Keep output under 150 words"]
- [Things to exclude, e.g., "Do not include legal opinions or medical advice"]
- [Tone rules, e.g., "Never use jargon the customer wouldn't understand"]
- [Edge cases, e.g., "If information is missing, state 'Not provided' — do not infer"]
```

---

## SECTION 5 — FORMAT
> **What to put here:** Exactly how the output should be structured. Specify structure (bullet list, table, JSON, paragraph), headings, labels, field names. The more precise, the more parseable the output.

```
Output format:
[Describe the exact structure — e.g., markdown table, JSON object, numbered list, plain paragraph]

Example structure:
[Paste a skeleton / schema of the expected output]
```

---

## SECTION 6 — EXAMPLES
> **What to put here:** 1–3 input/output pairs that demonstrate exactly what "correct" looks like. These are the single highest-leverage addition to any prompt. Show edge cases if they exist.

```
Examples:

### Example 1
Input: [sample input]
Output: [expected output]

### Example 2
Input: [sample input]
Output: [expected output]

### Example 3 (edge case, optional)
Input: [edge case input]
Output: [expected output handling the edge case]
```

---

## INPUT
> **What to put here:** The actual data/text for this specific run. Clearly delimited so the model knows where the instructions end and the data begins.

```
---INPUT START---
[Paste the actual input here]
---INPUT END---
```