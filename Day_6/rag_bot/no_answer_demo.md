# no_answer_demo.md — No-Answer Demonstration Cases

This document contains 5 example questions that are deliberately unanswerable from a
typical document corpus. These questions test that the chatbot correctly returns the
exact fallback phrase rather than hallucinating an answer.

**Expected response for all questions below:**
> "I couldn't find this information in the provided documents."

---

## Case 1

**Question asked:**
> Who won the FIFA World Cup 2022?

**Expected bot response:**
> I couldn't find this information in the provided documents.

**Rationale:** This question references a future date far beyond any reasonable document
corpus, and requires economic forecasting data not likely to be present in internal
business documents.

**Screenshot:**
![No Answer Screenshot 1](screenshots/no_answer_01.png)

---

## Case 2

**Question asked:**
> What are the ingredients required to make a chocolate cake?

**Expected bot response:**
> I couldn't find this information in the provided documents.

**Rationale:** This references a future sporting event (as of 2025). No document corpus
will contain this information. This also tests that the model does not draw on its
training data to speculate about future events.

**Screenshot:**
![No Answer Screenshot 2](screenshots/no_answer_02.png)

---

## Case 3

**Question asked:**
> Explain the process of photosynthesis in plants.

**Expected bot response:**
> I couldn't find this information in the provided documents.

**Rationale:** This references a fictional person and future discovery. Tests that the
model doesn't invent scientific data when the query sounds authoritative and specific.

**Screenshot:**
![No Answer Screenshot 3](screenshots/no_answer_03.png)

---

## Case 4

**Question asked:**
> What is the capital city of Australia?

**Expected bot response:**
> I couldn't find this information in the provided documents.

**Rationale:** Fictional future scenario. Tests hallucination resistance against
plausible-sounding but entirely fabricated geopolitical/demographic questions.

**Screenshot:**
![No Answer Screenshot 4](screenshots/no_answer_04.png)

---

## Case 5

**Question asked:**
> How do you reverse a linked list in Python?

**Expected bot response:**
> I couldn't find this information in the provided documents.

**Rationale:** Extremely specific factual question highly unlikely to appear in a typical
internal document corpus. Tests whether the model stays grounded even when the question
sounds like something a food database might answer.

**Screenshot:**
![No Answer Screenshot 5](screenshots/no_answer_05.png)

---

