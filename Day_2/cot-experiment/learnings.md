# CoT Experiment Learnings

**Date:** YYYY-MM-DD
**Model:** openai/gpt-oss-120b
**Experiment:** Insurance claim approval — 15 scenarios, 3 strategies

---

## What Broke and Why

### Errors encountered
<!-- List any errors that occurred, with scenario IDs and error types -->
- [ ] Rate limit (429) — scenario(s): ???, cause: ???
- [ ] Parse errors — scenario(s): ???, raw response pattern: ???
- [ ] Other: ???

### Patterns observed in failures
<!-- Did certain scenario types fail more? e.g., edge cases, exclusion-based denials -->

---

## Cost vs Accuracy Observations

| Strategy | Accuracy | Total Cost | Cost per correct answer |
|---|---|---|---|
| Direct | ??% | $??? | $??? |
| CoT | ??% | $??? | $??? |
| Self-Consistency | ??% | $??? | $??? |

### Was CoT worth the cost increase over Direct?
<!-- e.g., "CoT was 4× more expensive but only 10% more accurate — probably not worth it for simple cases" -->

### Was SC worth the cost increase over CoT?
<!-- e.g., "SC cost 5× more than CoT but only fixed 1 additional scenario" -->

---

## When CoT Helped vs Hurt Accuracy

### Scenarios where CoT was correct but Direct was wrong
<!-- List scenario IDs and briefly explain why reasoning helped -->
- S??: ???

### Scenarios where both Direct and CoT were wrong
<!-- These are the hardest cases — what made them hard? -->
- S??: ???

### Scenarios where Direct was correct but CoT was wrong
<!-- This happens! Sometimes explicit reasoning introduces errors. -->
- S??: ???

---

## When Self-Consistency Provided Diminishing Returns

### Did SC fix any scenarios that CoT alone got wrong?
<!-- List them here with the vote breakdown (e.g., "Yes: 3, No: 2 → Yes") -->

### Were there scenarios where SC consistently voted wrong?
<!-- i.e., the model was confidently wrong across all 5 runs -->

---

## Unexpected Behaviors

<!-- Anything that surprised you — unusual reasoning patterns, formatting quirks, etc. -->

---

## Actionable Conclusions

1. **Use Direct prompting when:** ???
2. **Use CoT when:** ???
3. **Use Self-Consistency when:** ???
4. **Prompt template improvements to try next:** ???