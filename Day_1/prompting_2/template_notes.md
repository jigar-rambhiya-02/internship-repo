# Prompt Template Notes — Why Each Section Matters

A 6-section prompt is not formality. Each section does a specific job.
Remove one and you don't save time — you create unpredictability.
Here's what breaks when you skip each one.

---

## 1. ROLE — "Who are you?"

**What it does:** Sets the model's knowledge domain, vocabulary level, and default communication style before the task begins.

**What breaks without it:**
The model defaults to a generic "helpful assistant" voice — which means it hedges more, uses vague language, and lacks the domain-specific judgment that makes outputs actually usable.

**Example of the problem:**
Prompt without role: *"Summarise this insurance claim."*
→ Output reads like a student essay. No mention of FIR requirements, IRDAI norms, or fast-track eligibility — all things an expert would flag automatically.

Prompt with role: *"You are a senior insurance claims analyst..."*
→ Output immediately references missing documentation requirements and recommends a specific next action. The role activated domain knowledge.

**Key insight:** Role is not a politeness ritual. It is a knowledge and register switch.

---

## 2. CONTEXT — "Why are you doing this?"

**What it does:** Tells the model who will read the output, what system it feeds into, and what domain rules apply. It answers "what world does this output live in?"

**What breaks without it:**
The model optimises for the wrong audience. It doesn't know if the reader is a lawyer, a 22-year-old mobile shopper, or a team lead skimming a morning queue. The output will be technically correct but calibrated for no one.

**Example of the problem:**
Prompt without context for product rewrite: *"Rewrite this product description in a luxury tone."*
→ Model produces copy that sounds premium but uses pricing cues and phrasing suited to a Western market, not Indian e-commerce. It might also ignore mobile-first reading patterns.

Prompt with context: *"Platform: Indian e-commerce. Audience: mobile shoppers, 22–40."*
→ Copy is punchy, front-loaded, and avoids verbosity that doesn't survive a 5-inch screen.

**Key insight:** Context is the difference between output that's correct and output that's deployable.

---

## 3. TASK — "What exactly do I want?"

**What it does:** Defines the primary action verb and, if needed, the ordered sub-steps. Removes ambiguity about what "done" looks like.

**What breaks without it:**
Models will fill task ambiguity with assumptions — and those assumptions are often wrong. A vague task produces a vague output. The model might summarise when you wanted classification, or classify when you wanted a recommendation.

**Example of the problem:**
Vague task: *"Do something useful with this email."*
→ Model writes a full reply to the email. That's not what the support team lead wanted. They wanted triage metadata.

Clear task: *"Classify the email as Urgent/Normal/Spam and extract sender intent, required action, and suggested owner."*
→ Exactly the structured data needed for the morning queue.

**Key insight:** If you can't say the task in one sentence with an action verb, you haven't defined it yet.

---

## 4. CONSTRAINTS — "What are the guardrails?"

**What it does:** Prevents the model's natural tendency toward completeness, elaboration, and hedging. It also handles edge cases explicitly so you don't get surprised in production.

**What breaks without it:**
Models will do "too much" — add disclaimers, invent missing details, produce outputs that are too long, too cautious, or structured inconsistently across runs. Edge cases get handled differently every time.

**Example of the problem:**
Claim summary without constraints:
→ Model invents a likely cause for missing data ("the claimant probably means..."), exceeds 200 words, and adds a legal disclaimer that makes the output unparseable by the dashboard system.

Claim summary with constraints: *"Write 'Not provided' for missing fields. Never infer. Maximum 200 words."*
→ Output is consistent, parseable, and honest about gaps.

**Key insight:** Constraints are not limitations on the model's creativity. They are the difference between outputs you can trust and outputs you have to check every time.

---

## 5. FORMAT — "What should the output look like?"

**What it does:** Specifies structure, so the output is immediately usable — parseable by code, scannable by humans, or pasteable into another system without reformatting.

**What breaks without it:**
Even when the content is correct, the structure will vary across runs. Sometimes a table, sometimes bullet points, sometimes prose. This makes downstream use (dashboards, copy-paste into CMS, CSV export) unreliable.

**Example of the problem:**
Email triage without format:
→ Run 1 gives a paragraph. Run 2 gives bullet points. Run 3 gives a table. All three are correct but none are consistent — the team lead has to re-read each one differently.

Email triage with format: *"Output must use bold field labels: Classification, Sender Intent, Key Action Required, Suggested Owner, Priority Reason."*
→ Every output is scannable in under 10 seconds. Same cognitive load every morning.

**Key insight:** Format is a contract between the prompt and the system that consumes the output. Without it, you've outsourced layout decisions to the model — and it will make different decisions every time.

---

## 6. EXAMPLES — "Show, don't just tell."

**What it does:** Demonstrates exactly what "correct" looks like — tone, length, structure, and edge case handling — in a way that instructions alone cannot convey.

**What breaks without it:**
Instructions describe the destination; examples show the route. Without examples, the model interprets ambiguous instructions in the most statistically common way — which is usually close but rarely exactly right. Edge cases get mishandled.

**Example of the problem:**
Product rewrite prompt without examples for "gen-z casual" tone:
→ Model writes something that's "casual" but reads like a brand intern trying to sound young. Slightly wrong register, slightly too long, too many complete sentences.

Product rewrite prompt with a gen-z example:
→ The model matches the exact register: contractions, incomplete sentences, confident irreverence. It saw what "casual" actually means in this context, not what the dictionary says.

**Key insight:** One well-chosen example is worth three constraint lines. Examples are the fastest way to close the gap between what you described and what you meant.

---

## The Removal Test — Quick Reference

| Section Removed | Failure Mode |
|---|---|
| **Role** | Generic voice, missing domain expertise, wrong register |
| **Context** | Correct content, wrong audience, wrong platform calibration |
| **Task** | Model guesses the goal; wrong action performed |
| **Constraints** | Inconsistent length, invented data, unhandled edge cases |
| **Format** | Correct content, inconsistent structure, not parseable downstream |
| **Examples** | Technically right but subtly wrong register, tone, or edge case handling |

---

## One More Thing: Section Order Matters

The sections above are ordered intentionally — each one narrows the model's solution space before the next instruction lands.

`Role → Context → Task → Constraints → Format → Examples`

Putting examples before constraints, or task before context, reduces their effectiveness. The model builds a mental model of the problem as it reads — give it the right scaffolding in the right order.