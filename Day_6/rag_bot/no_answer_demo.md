# no_answer_demo.md — No-Answer Demonstration Cases

This document contains 5 example questions that are deliberately unanswerable from a
typical document corpus. These questions test that the chatbot correctly returns the
exact fallback phrase rather than hallucinating an answer.

**Expected response for all questions below:**
> "I couldn't find this information in the provided documents."

---

## Case 1

**Question asked:**
> What is the projected GDP of Iceland in the year 2087?

**Expected bot response:**
> I couldn't find this information in the provided documents.

**Rationale:** This question references a future date far beyond any reasonable document
corpus, and requires economic forecasting data not likely to be present in internal
business documents.

**Screenshot:**
![No Answer Screenshot 1](screenshots/no_answer_01.png)
*(Replace this placeholder with your actual screenshot after running the chatbot.)*

---

## Case 2

**Question asked:**
> Who won the 2031 FIFA World Cup and what was the final score?

**Expected bot response:**
> I couldn't find this information in the provided documents.

**Rationale:** This references a future sporting event (as of 2025). No document corpus
will contain this information. This also tests that the model does not draw on its
training data to speculate about future events.

**Screenshot:**
![No Answer Screenshot 2](screenshots/no_answer_02.png)
*(Replace this placeholder with your actual screenshot after running the chatbot.)*

---

## Case 3

**Question asked:**
> What is the chemical formula for the compound discovered by Dr. Elena Voss in 2028?

**Expected bot response:**
> I couldn't find this information in the provided documents.

**Rationale:** This references a fictional person and future discovery. Tests that the
model doesn't invent scientific data when the query sounds authoritative and specific.

**Screenshot:**
![No Answer Screenshot 3](screenshots/no_answer_03.png)
*(Replace this placeholder with your actual screenshot after running the chatbot.)*

---

## Case 4

**Question asked:**
> What is the population of Mars colony Alpha as of December 2045?

**Expected bot response:**
> I couldn't find this information in the provided documents.

**Rationale:** Fictional future scenario. Tests hallucination resistance against
plausible-sounding but entirely fabricated geopolitical/demographic questions.

**Screenshot:**
![No Answer Screenshot 4](screenshots/no_answer_04.png)
*(Replace this placeholder with your actual screenshot after running the chatbot.)*

---

## Case 5

**Question asked:**
> What are the exact caloric contents of every item on the McDonald's menu in Papua New Guinea?

**Expected bot response:**
> I couldn't find this information in the provided documents.

**Rationale:** Extremely specific factual question highly unlikely to appear in a typical
internal document corpus. Tests whether the model stays grounded even when the question
sounds like something a food database might answer.

**Screenshot:**
![No Answer Screenshot 5](screenshots/no_answer_05.png)
*(Replace this placeholder with your actual screenshot after running the chatbot.)*

---

## How to Generate These Screenshots

1. Launch the chatbot: `python app.py`
2. Use the Gradio share URL from the terminal output.
3. Type each question above into the chat input.
4. Confirm the response matches "I couldn't find this information in the provided documents."
5. Take a screenshot of the full browser window showing the question and response.
6. Save to `screenshots/no_answer_0N.png` (N = 1 through 5).
7. Update the image paths in this document.
