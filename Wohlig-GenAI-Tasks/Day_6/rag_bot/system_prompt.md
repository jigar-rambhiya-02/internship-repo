# system_prompt.md — Grounding Prompt Specification

## Full System Prompt Text

The following is the exact text embedded in `src/generator.py` as the `SYSTEM_PROMPT` constant.
This is the first message in every Groq API request, sent as `role: "system"`.

```
You are a precise, grounded research assistant. You will be given a set of document chunks as your ONLY knowledge source for answering the user's question.

RULES — YOU MUST FOLLOW THESE WITHOUT EXCEPTION:
1. Answer ONLY using information explicitly present in the provided document chunks.
2. Every factual claim in your answer MUST include an inline citation in the format [doc_id:page].
3. If the provided chunks do not contain sufficient information to answer the question, you MUST respond with exactly: "I couldn't find this information in the provided documents." Do NOT attempt to answer from your training knowledge.
4. Do NOT infer, extrapolate, or guess. If it is not in the chunks, it does not exist for you.
5. Do NOT say things like "Based on my knowledge..." or "Generally speaking...". Only cite the chunks.
6. Be concise. Do not pad your answer with filler sentences.
```

---

## Rule-by-Rule Rationale

### Rule 1: Answer ONLY from provided chunks

**Failure mode prevented:** LLM knowledge bleeding.

LLMs are trained on vast corpora and will attempt to "fill in" answers using their parametric memory when the provided context seems insufficient. Without this rule, a question about "safety regulations" might cause the model to answer from general OSHA knowledge rather than the specific internal policy document you provided. Rule 1 establishes an absolute boundary: the chunks are the world.

### Rule 2: Every factual claim must include [doc_id:page]

**Failure mode prevented:** Untraceable assertions.

Without mandatory citations, the user has no way to verify where an answer came from, and the model has no incentive to stay grounded. Requiring a citation for *every* factual claim creates a verifiability chain: the user can open the source document, navigate to the cited page, and confirm the claim. It also acts as a self-consistency check — if the model cannot produce a citation, it should not be making the claim.

### Rule 3: Exact fallback phrase for insufficient context

**Failure mode prevented:** Confident hallucination on unanswerable questions.

This is the most critical rule. LLMs are trained to be helpful, which means they have a strong bias toward producing *some* answer even when they should say "I don't know." Without an explicit, exact fallback phrase, the model might hedge ("While I cannot be certain...") and then proceed to hallucinate. By specifying the exact required output, we can programmatically detect no-answer responses and the model's instruction-following is tested with precision.

### Rule 4: No inference or extrapolation

**Failure mode prevented:** Plausible-sounding deduction errors.

LLMs are capable of logical inference. If Chunk A says "X causes Y" and Chunk B says "Y leads to Z," the model might correctly deduce "X leads to Z" even if no chunk says this directly. In a general assistant, this is a feature. In a grounded research assistant, this is a liability: the user needs to know that every claim was stated explicitly in a source document, not derived by the model. Inference errors are particularly dangerous because they *look* correct.

### Rule 5: Prohibit hedge phrases from training data

**Failure mode prevented:** Implicit knowledge leakage disguised as hedging.

Phrases like "Based on my knowledge..." or "Generally speaking..." are signals that the model is drawing on parametric memory rather than the provided context. Explicitly prohibiting these phrases eliminates a common escape route the model uses to blend its training knowledge into responses.

### Rule 6: Be concise

**Failure mode prevented:** Padding and hallucination by verbosity.

Longer answers create more surface area for hallucination. If the model is told to elaborate, it will often add plausible-sounding details not present in the chunks. Requiring concision keeps the model anchored to exactly what the chunks say.

---

## Citation Format Specification

### Format

```
[doc_id:page]
```

Where:
- `doc_id` is the filename of the source document **without its extension**.
- `page` is the page number (for PDFs, 1-indexed) or chunk index (for TXT files).

### Examples

| Scenario | Citation |
|---|---|
| From `annual_report.pdf`, page 4 | `[annual_report:4]` |
| From `safety_manual.pdf`, page 11 | `[safety_manual:11]` |
| From `meeting_notes.txt`, chunk 2 | `[meeting_notes:2]` |
| From `Q3_analysis.pdf`, page 23 | `[Q3_analysis:23]` |

### Example Answer with Citations

**User question:** What were the revenue figures mentioned in the report?

**Model response:**
> Revenue for Q3 2024 reached $4.2 million [annual_report:4], representing a 12% increase over Q2 figures [annual_report:4]. The full-year projection was revised upward to $16.8 million based on this performance [annual_report:7].

Each sentence contains a citation. No sentence makes a factual claim without one.

### What Makes a Good doc_id

The `doc_id` is set during ingestion as `Path(filename).stem`. This means:
- `financial_report_2024.pdf` → `doc_id = "financial_report_2024"`
- `HR Policy Manual v3.pdf` → `doc_id = "HR Policy Manual v3"`
- `notes.txt` → `doc_id = "notes"`

**Recommendation for interns:** Use clean, descriptive filenames without spaces (use underscores instead). Example: `safety_manual_2024.pdf` → `[safety_manual_2024:8]`.
