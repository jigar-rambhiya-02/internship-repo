# Test Briefs for Meta-Prompter

These are intentionally vague user requests — the kind a real stakeholder might
send in a Slack message. The meta-prompt must resolve the ambiguity and produce
a prompt a developer could hand directly to an LLM with confidence.

---

## Brief 1

**Brief:** "extract data from PDFs"

**Why it's vague:** It doesn't specify what *kind* of data (tables, text, metadata,
form fields), what the PDFs contain (invoices, research papers, contracts), what
format the extracted data should take, or what the downstream use case is.

---

## Brief 2

**Brief:** "classify support emails"

**Why it's vague:** It omits the taxonomy of categories, how to handle ambiguous
emails that could belong to multiple classes, what to do with spam, whether
confidence scores are needed, and whether the output feeds a human or an automation.

---

## Brief 3

**Brief:** "write product descriptions"

**Why it's vague:** It gives no information about the product category, target
audience, tone (formal vs. playful), required length, SEO requirements, or which
product attributes must always be included.

---

## Brief 4

**Brief:** "summarize legal documents"

**Why it's vague:** Legal documents vary enormously (contracts, briefs, statutes,
NDAs); it's unclear who the reader is (lawyer, client, executive), what the
acceptable summary length is, and whether the model should flag risky clauses or
just neutrally condense.

---

## Brief 5

**Brief:** "translate marketing copy"

**Why it's vague:** It doesn't name the target language, doesn't specify whether
to translate literally or localize culturally, doesn't say whether brand voice
should be preserved or adapted, and doesn't address what to do with idioms,
slogans, or trademarked terms.