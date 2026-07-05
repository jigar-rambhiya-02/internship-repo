# Day 1

## Day 1 GOAL: Learn how to pick the right Gemini model for a client task by comparing cost vs quality vs speed

Prompting Foundations + Prompt Types

Task
CONCEPT: Gemini comes in 3 main tiers: Gemini 3 Pro (smartest, slowest, most expensive), Flash (balanced), Flash-Lite (fastest, cheapest, lower quality). For client projects, picking the right tier saves money or improves user experience.

STEPS:
1. Pick one realistic task - e.g. summarize a 1-page document into a 3-bullet summary. Prepare 20 sample documents (can be news articles, Wikipedia paragraphs, anything similar in size).
2. Write one prompt that works for the task.
3. Run the same prompt + 20 inputs through Gemini 3 Pro, Flash, and Flash-Lite. Use a timer to measure latency. Track input/output tokens (the SDK returns these in usage_metadata).
4. Compute cost per call using current Gemini pricing (input $/1M tokens × input tokens + output $/1M tokens × output tokens).
5. Use Gemini Pro to score each output for quality on a 1–5 scale (this is called 'LLM-as-judge').
6. Build a recommendation: which model would you pick for this task, and why.

Deliverable:-
1) /model_selection/run.py - script that runs all 3 models on the same 20 inputs and logs results
2) /model_selection/results.csv - columns: input_id, model, latency_ms, input_tokens, output_tokens, cost_usd, quality_score_1to5, notes
3) /model_selection/recommendation.md (1 page): average latency/cost/quality per model, your recommended model for this task type, and a simple decision rule mapping task characteristics → model (e.g. 'high-volume + low-stakes → Flash-Lite')

Reference:-
ai.google.dev/gemini-api/docs/models



## Day 1 GOAL: Understand the 3 main prompt styles and when to use each

Prompting Foundations + Prompt Types

CONCEPTS:
• Zero-shot - you only describe the task, no examples (e.g. 'Classify this ticket: ...')
• Few-shot - you give 3–5 example input→output pairs before the real input
• Role-based - you give the model a persona/role (e.g. 'You are a senior customer support analyst...')

STEPS:
1. Create 30 fake customer support tickets across 8 categories (Refund, Shipping, Login, Payment, Account, Product Quality, Order Change, Other). You can generate them using Gemini itself.
2. Manually label each ticket with the correct category (this is your 'ground truth').
3. Write 3 different prompts - one for each style - that classify a ticket into one of the 8 categories.
4. Run each prompt on all 30 tickets using Gemini Flash. Save predictions.
5. Compare predictions to ground truth. Calculate accuracy for each style.
6. Write a short note: which style worked best, and why you think so.


1) /prompting/styles_eval.csv - columns: ticket_id, ticket_text, ground_truth, zero_shot_pred, few_shot_pred, role_based_pred, zero_correct (bool), few_correct (bool), role_correct (bool)
2) /prompting/styles_finding.md (1 page): accuracy table for all 3 styles, 3 example tickets where each style won, 3 where each style failed, your conclusion on when to use which style
3) /prompting/prompts/ - zero_shot.txt, few_shot.txt, role_based.txt (the actual prompts you used)
4) Commit everything to your bootcamp Git repo


## Day 1 GOAL: Build a reusable prompt template the team can use on any client project.

Prompting Foundations + Prompt Types

Task:-
CONCEPT: A good prompt has 6 standard sections - Role (who the model is acting as), Context (background info), Task (what you want done), Constraints (rules/limits), Format (how output should look), Examples (1–3 input/output pairs). When you fill all 6, prompts become much more reliable.

STEPS:
1. Create a markdown template with all 6 sections, each with a 1-line explanation of what to put there.
2. Pick 3 different client-style tasks: (a) summarize an insurance claim, (b) rewrite a product description in a different tone, (c) sort customer emails into urgent/normal/spam.
3. For each task, fill in the template (write the actual prompt).
4. Create 3 input examples per task, run the prompt, save the outputs.
5. Write a short note on what makes each section important - try removing one section at a time and see what breaks.

Deliverable:-
1) /prompting/wohlig_prompt_template.md - the template with placeholders and section explanations
2) /prompting/applied/ folder with 3 subfolders (claim_summary, product_rewrite, email_triage). Each subfolder has: prompt.txt (the filled template), inputs/ (3 input examples), outputs/ (3 outputs)
3) /prompting/template_notes.md: short notes on why each of the 6 sections matters, with examples of what goes wrong when you skip one

Reference:-
ai.google.dev/gemini-api/docs/system-instructions


# Day 2

## Day 2 GOAL: Learn Chain-of-Thought (CoT) prompting and when it's worth the extra cost

Advanced Prompting - CoT, Chaining, Meta-Prompting

Task:-
CONCEPTS:
• Direct prompting - just ask the question, model answers immediately
• Chain-of-Thought - you tell the model 'Think step by step before answering' so it works through the logic first. Usually improves accuracy on reasoning tasks.
• Self-consistency - run the same CoT prompt 5 times at higher temperature (0.7), then take the majority answer. Even more accurate, but 5x the cost.

STEPS:
1. Create 15 simple reasoning scenarios. Use insurance claim approval as the domain: 'Customer X had policy Y, claimed Z, here are the rules... should claim be approved? Yes/No'. Make sure each has a clear correct answer.
2. Write 3 versions of the prompt: (a) direct ('Answer Yes or No'), (b) CoT ('Think step by step, then answer Yes or No'), (c) self-consistency (run CoT 5 times at temp=0.7, take majority).
3. Run all 15 scenarios through each prompt. Save answers + costs.
4. Compare accuracy. Compute cost per correct answer.
5. Write a simple rule: 'Use CoT when... use self-consistency when...'

Deliverable:-
1) /cot/scenarios.jsonl - 15 reasoning scenarios with ground-truth answer for each
2) /cot/results.csv - columns: scenario_id, direct_answer, direct_correct, cot_answer, cot_correct, sc_answer, sc_correct, direct_cost_usd, cot_cost_usd, sc_cost_usd
3) /cot/cot_decision_rule.md: accuracy table (direct vs CoT vs self-consistency), cost-per-correct-answer for each, your written rule for when each technique is worth using
4) /cot/prompts/ - direct.txt, cot.txt, sc.txt

Reference:-
promptingguide.ai/techniques/cot

## Day 2 GOAL: Learn prompt chaining - connecting multiple prompts so one's output feeds the next. This is how Wohlig's PocketStudio (HDFC Life / Croma) builds creative content

Advanced Prompting - CoT, Chaining, Meta-Prompting

Task:-
CONCEPT: A single complex prompt often fails (the model tries to do too much). Splitting into 3 small focused prompts usually works much better. Each step is reliable on its own.

PIPELINE TO BUILD (3 steps):
• Step 1 - Extract: take a product brief (free text) and extract structured attributes (product_name, category, key_features, target_audience) using response_schema.
• Step 2 - Generate: feed the attributes JSON into a second prompt that generates 3 different ad copy variants.
• Step 3 - Select: feed the 3 variants into a third prompt that picks the best one based on simple brand rules (e.g. 'no superlatives like best/cheapest') and explains why.

STEPS:
1. Write the 3 prompts as separate files.
2. Build pipeline.py that runs Step 1 → Step 2 → Step 3 in order, passing data between them.
3. Write 5 product briefs (e.g. for fictional brands).
4. Run the full pipeline on all 5 briefs. Save every intermediate output (so you can debug if a step fails).
5. Note: what happened when Step 1 returned wrong attributes - did Step 2 still work? What did you learn about error handling across steps?

Deliverable:-
1) /chaining/prompts/ - extract.txt, generate.txt, select.txt (3 separate prompt files)
2) /chaining/pipeline.py - orchestrates the 3 steps
3) /chaining/brand_rules.md - the simple brand rules used in Step 3
4) /chaining/runs/ - 5 run folders, each containing: input_brief.txt, step1_attributes.json, step2_variants.json, step3_winner.json
5) /chaining/learnings.md: what broke during testing, how errors in Step 1 affected Step 2, what you learned about splitting tasks into smaller prompts


## Day 2 GOAL: Learn meta-prompting - using Gemini to write prompts for you

Advanced Prompting - CoT, Chaining, Meta-Prompting

Task:-
CONCEPT: A 'meta-prompt' is a prompt that takes a vague user request (like 'I want to extract data from PDFs') and produces a high-quality structured prompt for that task. This saves time when starting a new client project.

STEPS:
1. Write a meta-prompt that takes a vague brief and outputs a full prompt following the Day-1 template (Role/Context/Task/Constraints/Format/Examples). The meta-prompt itself should give Gemini clear instructions about what makes a good prompt.
2. Save it as meta_prompt.txt.
3. Build meta_prompter.py - a CLI that takes a vague brief and outputs a generated prompt.
4. Test it on 5 different vague briefs (e.g. 'extract data from PDFs', 'classify support emails', 'write product descriptions', 'summarize legal documents', 'translate marketing copy').
5. For each generated prompt: check if it has all 6 sections, rate its quality 1–5 (you can also use Gemini-as-judge for this), note what's missing or weak.
6. Write a short note: when is meta-prompting useful vs when is it faster to write prompts manually?

Deliverable:-
1) /meta/meta_prompt.txt - the actual meta-prompt you wrote
2) /meta/meta_prompter.py - CLI tool
3) /meta/test_briefs.md - 5 vague briefs
4) /meta/generated_prompts/ - the 5 generated prompts
5) /meta/judge_scorecard.csv - brief_id, generated_prompt_quality_1to5, has_all_6_sections (bool), what_was_missing
6) /meta/findings.md: when meta-prompting helps vs when manual prompting is faster


# Day 3

## Day 3 GOAL: Build your first multi-tool agent using Gemini's function calling

Structured Outputs + Function Calling (Client Extraction Patterns)

Task:-
CONCEPT: Function calling lets you give Gemini a list of Python functions it can request to be called. Gemini decides which to call and with what arguments. You execute and pass the result back. This is the foundation of every agent we build.

BUILD A CUSTOMER-SERVICE AGENT WITH 4 TOOLS:
• get_order(order_id) - returns order details from a fake JSON databa
• get_shipping(order_id) - returns shipping status
• check_refund_policy(category) - returns refund rules for a product category
• escalate_to_human(reason) - returns a confirmation that an agent will follow up

STEPS:
1. Create fake_orders.json with 20+ orders in varied states (delivered/in-transit/returned/disputed).
2. Implement the 4 functions as plain Python.
3. Build agent.py: send user message + tool definitions to Gemini, loop - execute the tool Gemini asks for, send result back, repeat until Gemini responds with final text answer.
4. Write 10 test queries: 3 single-tool (e.g. 'What's the status of order #123?'), 3 needing 2+ tools, 2 multi-turn conversations, 2 that should trigger escalation (e.g. angry customer).
5. Run all 10. Verify the agent calls the right tools and escalates when it should.


Deliverable:-
1) /fc_agent/agent.py - main agent loop
2) /fc_agent/tools.py - the 4 tool implementations
3) /fc_agent/fake_orders.json - 20+ fake orders
4) /fc_agent/test_queries.md - 10 test queries categorized (single-tool / multi-tool / escalation)
5) /fc_agent/test_results.md - for each query: tools called, in what order, final response, did it match expected behavior (PASS/FAIL)
6) /fc_agent/escalation_logic.md: what triggers escalation, what context the agent passes when escalating


Reference:-
ai.google.dev/gemini-api/docs/function-calling

## Day 3 GOAL: Build a document extractor - one of the most common client requests at Wohlig

Structured Outputs + Function Calling (Client Extraction Patterns)

Task:-
CONCEPT: response_schema lets you force Gemini to return JSON in a specific shape. Combined with Pydantic models in Python, you get type-safe extraction with validation. This is what we build for KYC, claim forms, invoices, etc.

STEPS:
1. Pick ONE document type: insurance claim form OR B2B invoice OR medical lab report OR KYC document.
2. Design the output schema as a Pydantic model with: 5–10 main fields, at least 1 nested object (e.g. address with street/city/pin), at least 1 list (line items), at least 1 enum field (status), and at least 1 optional field that may or may not appear.
3. Generate or find 10 sample documents (can be synthetic - generate fake samples using Gemini itself).
4. Manually create ground-truth JSON for each sample - what the perfect extraction should look like.
5. Build main.py that takes a file path and returns the extracted JSON via Gemini multimodal + response_schema.
6. Run on all 10 samples. Compare extracted vs ground truth field-by-field.
7. Write an accuracy summary: which fields work well, which ones break, why.

Deliverable:-
1) /extractor/ project: main.py (CLI: file_path → JSON), schema.py (Pydantic model)
2) /extractor/samples/ - 10 sample documents (PDFs or images)
3) /extractor/ground_truth.jsonl - expected JSON output for each sample
4) /extractor/field_accuracy.csv - one row per field per sample: sample_id, field_name, extracted_value, ground_truth_value, exact_match (bool)
5) /extractor/accuracy_summary.md: per-field accuracy %, which fields fail most, common error types, ideas to improve
6) README.md with run instructions

Reference:-
ai.google.dev/gemini-api/docs/structured-output

## Day 3 GOAL: Make your structured outputs reliable in production by adding self-repair

Structured Outputs + Function Calling (Client Extraction Patterns)

Task:-
CONCEPT: Even with response_schema, Gemini sometimes returns invalid JSON (wrong type, missing field, etc.). In production, you can't just fail - you should let the model try again with the error message as feedback. Usually it fixes itself on the second try.

STEPS:
1. Define a simple Pydantic model - for example, ContactCard with name (str), email (valid email), phone (10 digits), address (nested object with city + pincode).
2. Write repair_loop.py - a function that:
   a) Calls Gemini with a prompt + response_schema
   b) Tries to parse the response into your Pydantic model
   c) If parsing fails, builds a new prompt including the original request + Gemini's previous output + the validation error message, and retries
   d) Max 3 retries, then gives up
3. Prepare 20 messy real-world inputs - e.g. OCR'd business cards with typos, mixed languages, missing fields, garbled formatting. You can generate these with Gemini.
4. Run all 20 inputs through repair_loop.
5. Track: how many succeeded on first try, how many succeeded after retry, how many failed all 3 attempts, total cost.
6. Write a comparison: what's the success rate without repair (single attempt) vs with repair?

Deliverable:-
1) /self_repairz/repair_loop.py - the retry wrapper function
2) /self_repair/schema.py - the Pydantic model
3) /self_repair/inputs/ - 20 messy inputs
4) /self_repair/results.csv - input_id, first_try_valid (bool), final_valid (bool), num_retries, errors_seen, total_cost
5) /self_repair/comparison.md: success rate without repair vs with repair, common error types fixed, cost vs success rate trade-off

# Day 4

## Day 4 GOAL: Build a creative image-generation pipeline - exactly the pattern behind Wohlig's PocketStudio work for Croma and HDFC Life

Multimodal - Vision, Image Gen, Video (PocketStudio Pattern)

Task:-
CONCEPT: Take one plain product photo + a short brief, generate 3 styled variants using Nano Banana Pro (different background/mood/season). Add a brand-guideline check so we never ship outputs that violate brand rules.

STEPS:
1. Write brand_guidelines.md - a simple set of rules (e.g. allowed background colors, prohibited objects, tone keywords like 'premium', 'aspirational').
2. Pick or create 5 plain product photos (e.g. a shoe, a watch, a kitchen appliance - keep it simple).
3. For each, write a brief.json - { product: 'X', desired_mood: 'festive', desired_background: 'studio with warm lights' }.
4. Build pipeline.py:
   a) Read input image + brief
   b) Call Nano Banana Pro 3 times with different style variations
   c) For each output, call Gemini to check it against brand guidelines (pass/fail with reasoning)
   d) Save all 3 variants + brand check results to GCS
5. Run the pipeline on all 5 products.
6. Track cost per run (Nano Banana per-image cost + Gemini brand-check cost).

Deliverable:-
1) /creative/pipeline.py - full pipeline CLI
2) /creative/brand_guidelines.md - your fake but realistic brand rules
3) /creative/runs/ - 5 SKU folders, each with: input.jpg, brief.json, variant_1.jpg, variant_2.jpg, variant_3.jpg, brand_check.json (with pass/fail + reasoning per variant)
4) /creative/prompts/ - the Nano Banana prompts + brand-check prompt
5) /creative/cost_log.csv: run_id, variants_generated, gen_cost_usd, brand_check_cost_usd, total_cost_usd

Reference:-
cloud.google.com/vertex-ai/generative-ai/docs/image/overview

## Day 4 GOAL: Generate a product video reel using Veo - this is the video side of PocketStudio

Multimodal - Vision, Image Gen, Video (PocketStudio Pattern)

Task:-
CONCEPT: Veo turns a text prompt (and optionally a reference image) into a short video. Good Veo prompts use cinematic language - camera moves, lighting, mood. Bad prompts produce generic results. You learn by iterating.

STEPS:
1. Pick a product (a real or fictional one - e.g. a sneaker).
2. Write a 30-word script: hook + product showcase + call-to-action.
3. Find or generate 1 reference image of the product.
4. Write your first Veo prompt. Generate a 15-second video. Save as v1.
5. Critique v1 - what's wrong? Wrong camera angle? Generic background? Awkward motion?
6. Rewrite the prompt with cinematic language ('slow dolly-in', 'golden hour lighting', 'shallow depth of field'). Generate v2.
7. Critique again, rewrite, generate v3.
8. Write down 5–7 concrete prompting lessons for Veo that the team can reuse.

Deliverable:-
1) /veo/generate.py - script that calls Veo with prompt + reference image
2) /veo/iterations/ - v1/, v2/, v3/ folders, each with: prompt.txt, output.mp4, critique.md
3) /veo/final_prompt.md - the best prompt with annotations explaining each phrase
4) /veo/prompting_lessons.md: 5–7 Veo prompting tips (camera language, motion words, lighting cues, what to avoid)

Reference:-
cloud.google.com/vertex-ai/generative-ai/docs/video/overview

## Day 4 GOAL: Build a vision-based document extractor that handles real-world image quality issues - the kind of pipeline Apollo or KYC clients need.

Multimodal - Vision, Image Gen, Video (PocketStudio Pattern)
 
Task:-
CONCEPT: Take one plain product photo + a short brief, generate 3 styled variants using Nano Banana Pro (different background/mood/season). Add a brand-guideline check so we never ship outputs that violate brand rules.
 
STEPS:
1. Write brand_guidelines.md - a simple set of rules (e.g. allowed background colors, prohibited objects, tone keywords like 'premium', 'aspirational').
2. Pick or create 5 plain product photos (e.g. a shoe, a watch, a kitchen appliance - keep it simple).
3. For each, write a brief.json - { product: 'X', desired_mood: 'festive', desired_background: 'studio with warm lights' }.
4. Build pipeline.py:
   a) Read input image + brief
   b) Call Nano Banana Pro 3 times with different style variations
   c) For each output, call Gemini to check it against brand guidelines (pass/fail with reasoning)
   d) Save all 3 variants + brand check results to GCS
5. Run the pipeline on all 5 products.
6. Track cost per run (Nano Banana per-image cost + Gemini brand-check cost).
 
Deliverable:-
1) /creative/pipeline.py - full pipeline CLI
2) /creative/brand_guidelines.md - your fake but realistic brand rules
3) /creative/runs/ - 5 SKU folders, each with: input.jpg, brief.json, variant_1.jpg, variant_2.jpg, variant_3.jpg, brand_check.json (with pass/fail + reasoning per variant)
4) /creative/prompts/ - the Nano Banana prompts + brand-check prompt
5) /creative/cost_log.csv: run_id, variants_generated, gen_cost_usd, brand_check_cost_usd, total_cost_usd
 
Reference:-
cloud.google.com/vertex-ai/generative-ai/docs/image/overview


# Day 5

## Day 5 GOAL: Build a production-style vector search index - the foundation for all RAG work

Embeddings + Vector Search (Production-Style Indexing)

Task:-
CONCEPT: An 'embedding' is a numerical fingerprint of a piece of text. Similar-meaning texts have similar embeddings. A vector index lets you search by meaning, not keywords. Vertex AI Vector Search is Google's managed product for this.

STEPS:
1. Pick a corpus: 200+ PDFs from one source (suggestions: arXiv ML papers, RBI circulars, NSE annual reports - all free).
2. Build ingest.py:
   a) Parse each PDF into text (use pypdf)
   b) Chunk each PDF (start with 512-token chunks)
   c) Embed each chunk using Gemini Embedding API
   d) Push chunks + embeddings + metadata (doc_id, year, doc_type, page_number) to Vertex AI Vector Search
3. Build query.py - accepts a question and optional metadata filters, returns top-K chunks.
4. Build a manifest CSV listing all your indexed docs.
5. Test 10 example queries showing metadata filtering works (e.g. 'inflation from 2023 reports only').

Deliverable:-
1) /vvs/ingest.py - chunking + embedding + upload
2) /vvs/query.py - query with optional filters
3) /vvs/corpus_manifest.csv - doc_id, title, year, doc_type, num_pages, num_chunks
4) /vvs/filtered_queries.md - 10 example queries with filter + top-5 retrieved chunks shown
5) /vvs/setup.md - README: index config, embedding dimensions, distance metric, deploy commands

Reference:-
cloud.google.com/vertex-ai/docs/vector-search

## Day 5 GOAL2 : Figure out the best chunking strategy for your corpus - this single decision often makes or breaks a RAG system

Embeddings + Vector Search (Production-Style Indexing)

Task:-
CONCEPT: 'Chunking' = splitting documents into smaller pieces before indexing. Too small = pieces lose context. Too big = retrieval gets noisy. Different strategies exist:
• Fixed-size - every chunk is N tokens, ignore structure
• Sentence-aware - split on sentence boundaries, group into chunks ~N tokens
• Semantic - split on heading/section boundaries, keep related content together

STEPS:
1. Implement all 3 chunkers as separate Python functions in strategies.py.
2. For each, re-index your Day-5 corpus (or a subset of 50 docs to save time/cost).
3. Build a test set: 25 questions where you know the exact chunk(s) that should answer them (mark the ground-truth chunk_ids).
4. Run all 25 questions through each chunking strategy. Measure recall@5 and recall@10 (= did the right chunk appear in the top 5/10 results?).
5. Tabulate and pick a winner. Explain why.

Deliverable:-
1) /chunking/strategies.py - 3 chunker functions: fixed_size, sentence_aware, semantic
2) /chunking/test_set.jsonl - 25 questions with ground-truth chunk_ids
3) /chunking/eval.py - runner that scores all 3 strategies
4) /chunking/results.csv - question_id, fixed_recall_5, fixed_recall_10, sentence_recall_5, sentence_recall_10, semantic_recall_5, semantic_recall_10
5) /chunking/winner.md: aggregate scores, your recommended chunker for this corpus type, and a simple rule of thumb (e.g. 'use semantic when docs have headings, fixed when not')

## Day 5 GOAL 3: Compare Vertex AI Vector Search vs BigQuery vector search - for Wohlig clients we need to know when to recommend each.

Embeddings + Vector Search (Production-Style Indexing)

Task:-
CONCEPT: BigQuery now supports VECTOR_SEARCH natively. If a client's data is already in BigQuery, this is often simpler and cheaper than setting up a separate vector DB. But it has trade-offs.

STEPS:
1. Take the same corpus as Day 5 Task 1 (or a 50-doc subset).
2. Create a BigQuery table with columns: chunk_id, doc_id, page, text, embedding (VECTOR type). Use ML.GENERATE_EMBEDDING or compute embeddings in Python and load.
3. Build a CREATE VECTOR INDEX query.
4. Write query.py that runs the same 25 questions from the chunking task.
5. Time each query (you can read query duration from BQ job metadata).
6. Compare to Vertex AI Vector Search: latency per query, recall@10, cost (look up GB-stored pricing for BQ vs the Vertex AI VS deployment cost).
7. Write a 1-page recommendation: when to choose each.


Deliverable:-
1) /bq_vector/ingest.sql + ingest.py - table creation, embedding, index build
2) /bq_vector/query.py - runs the 25 questions
3) /comparison/results.csv - question_id, vvs_latency_ms, bq_latency_ms, vvs_recall_10, bq_recall_10
4) /comparison/cost_breakdown.md - setup cost, query cost per 1000, storage cost (numbers for both)
5) /comparison/recommendation.md (1 page): when to pick VVS, when to pick BQ vector, decision criteria (data location, latency needs, scale, cost)

Reference:-
cloud.google.com/bigquery/docs/vector-search

# Day 6

## Day 6 GOAL 1: Build a RAG chatbot that cites every claim - exactly the pattern behind Meesho Memory and Apollo content search

RAG with Grounding + Eval (Production-Grade)

Task:-
CONCEPT: RAG = Retrieval-Augmented Generation. Step 1: retrieve relevant chunks from your vector index. Step 2: pass those chunks + the user's question to Gemini and ask it to answer using ONLY those chunks, with citations. Step 3: if the chunks don't contain the answer, the model must say 'I don't know' - never hallucinate.

STEPS:
1. Use your Day-5 Vertex AI Vector Search index.
2. Build retriever.py - takes a question, returns top-5 chunks with their metadata.
3. Build generator.py - takes question + retrieved chunks, calls Gemini with a careful prompt that:
   a) Tells the model to use ONLY the provided chunks
   b) Requires inline citations like [doc_id:page]
   c) Tells the model to say 'I couldn't find this information in the provided documents' if nothing relevant is found
4. Build app.py with Gradio - simple chat UI.
5. Test with 5 questions that SHOULDN'T have answers in your corpus. Take screenshots showing the bot correctly says 'I don't know' instead of making up answers.
6. Deploy the Gradio app with share=True for a temporary public URL.

Deliverable:-
1) /rag_bot/ project: app.py (Gradio), retriever.py, generator.py
2) /rag_bot/system_prompt.md - the careful grounding prompt with rules
3) /rag_bot/no_answer_demo.md - 5 out-of-corpus questions + screenshots of 'I don't know' responses
4) /rag_bot/screenshots/ - 5 example conversations showing proper inline citations
5) Gradio share URL (valid 72 hours) pasted in this row's Notes column

Reference:-
cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview

## Day 6 GOAL 2: Build a RAG evaluation harness - the #1 most valuable skill for client work. Anyone can build a RAG demo; almost nobody measures it properly

RAG with Grounding + Eval (Production-Grade)

Task:-
CONCEPT: There are 4 standard RAG quality metrics, all scored 0–1 by an LLM judge:
• Faithfulness - does the answer stick to the retrieved context (no hallucinations)?
• Answer relevance - does the answer actually address the question?
• Context precision - were the retrieved chunks useful (or full of irrelevant junk)?
• Context recall - did we retrieve everything we needed to answer the question?

STEPS:
1. Build test_set.jsonl - 30 questions with: question text, ground-truth answer (you write this manually after reading the corpus), ground-truth chunk_ids (which chunks should ideally be retrieved).
2. Write 4 separate judge prompts (one per metric). Each takes (question, answer, context) and returns a 0–1 score with reasoning.
3. Build run_eval.py - runs all 30 questions through the Day-6 RAG bot, then scores all 4 metrics for each using Gemini-as-judge.
4. Save results.csv with all scores.
5. Write eval_report.md - aggregate scores, the 3 best answers, the 3 worst answers (with reasons), and prioritized improvements.

Deliverable:-
1) /eval/test_set.jsonl - 30 questions with ground-truth answer + ground-truth chunk_ids
2) /eval/judges.py - 4 judge prompts as separate functions, each returns score 0–1 + reasoning
3) /eval/run_eval.py - full eval pipeline
4) /eval/results.csv - question_id, question, answer, faithfulness, answer_relevance, context_precision, context_recall, avg_score
5) /eval/eval_report.md: aggregate scores, score distribution (with histograms if possible), 3 best + 3 worst cases with full transcripts and root-cause notes, ranked list of improvements

Reference:-
docs.ragas.io

## Day 6 GOAL 3: Make your RAG significantly better using 2 well-known production techniques.

RAG with Grounding + Eval (Production-Grade)

Task:-
CONCEPTS:
• Re-ranking - first retrieve top 20 chunks by embedding similarity, then use a second model (Vertex AI Ranking API) to re-score and keep top 5. The re-ranker is slower but much more accurate.
• Contextual retrieval (Anthropic's idea) - before indexing, you prepend each chunk with a 1-line context summary generated by Gemini (e.g. 'This chunk is from section 3 of the 2023 annual report discussing operating expenses'). This makes chunks more searchable.

STEPS:
1. Add re-ranker: modify retriever to fetch top 20, then call Vertex AI Ranking API to keep top 5.
2. Add contextual retrieval: write a contextualizer.py that processes the corpus, adds a 1-line context prefix to each chunk, then re-embeds and re-indexes.
3. Rerun the Day-6 eval harness on 3 configurations: naive RAG, with re-ranker only, with contextual retrieval only, with both.
4. Tabulate the improvements (or regressions). Note any unexpected results.

Deliverable:-
1) /production_rag/reranker.py - wraps retriever, fetches 20 → re-ranks to 5
2) /production_rag/contextualizer.py - script to re-index with context prefixes
3) /production_rag/results.csv - question_id, naive_faithfulness, naive_relevance, ..., reranked_*, contextual_*, both_* (4 metrics × 4 configs)
4) /production_rag/lift_report.md: lift % per technique per metric, extra cost added by each technique (more API calls / one-time corpus prep), final recommendation: which combo to ship to clients

Reference:-
anthropic.com/news/contextual-retrieval


# Day 7

## Day 7 GOAL 1: Add hybrid search to your RAG bot to handle keyword-heavy queries.

Advanced RAG - Hybrid + Text2SQL (BI Co-Pilot Pattern)

Task:-
CONCEPTS:
• Dense search (what you already have) - finds chunks by meaning. Great for semantic questions.
• BM25 search - old-school keyword search. Great when users search exact terms like 'policy ABC-2024-117' or 'Section 80C'.
• Hybrid - run both, then merge results using Reciprocal Rank Fusion (RRF). RRF is a simple formula that gives a chunk a score based on its rank in each list, then sums them.

STEPS:
1. Build a BM25 index alongside your vector index (use rank_bm25 Python library).
2. Write rrf.py - given two ranked lists, output a merged list using the RRF formula: score(chunk) = sum over both lists of 1/(60 + rank).
3. Modify retriever to: run dense search → top 20, run BM25 → top 20, merge via RRF → final top 5.
4. Extend your test set: keep the original 30 questions, add 10 keyword-heavy ones (e.g. 'tell me about clause 8.2.1', 'what's the rate for HS code 6403').
5. Rerun the eval harness for dense-only vs hybrid. Tabulate by query type.
6. Write a finding: when does hybrid actually beat dense? When is it overkill?

Deliverable:-
1) /hybrid/bm25_index.py - builds BM25 index from the corpus
2) /hybrid/rrf.py - RRF merge function
3) /hybrid/retriever_hybrid.py - combined retriever
4) /hybrid/test_set_extended.jsonl - original 30 + 10 keyword-heavy questions
5) /hybrid/results.csv - question_id, query_type (semantic/keyword/mixed), dense_recall, bm25_recall, hybrid_recall
6) /hybrid/when_hybrid_wins.md: query-type breakdown, client scenarios where each is recommended


## Day 7 GOAL 2: Build a text-to-SQL BI co-pilot - the core pattern behind Wohlig's Jindal Leadership Co-Pilot.

CONCEPT: User asks a question in English. The agent:
  1. Reads the BigQuery table schemas
  2. Generates SQL
  3. Validates the SQL (using BQ dry-run mode - checks syntax without running)
  4. Executes the query
  5. Returns a natural-language summary + suggests a chart type

STEPS:
1. Pick a public BigQuery dataset: bigquery-public-data.new_york_taxi_trips or bigquery-public-data.stackoverflow. Document why you picked it and its key tables.
2. Build schema_loader.py - fetches table schemas (column names, types, sample values) and formats them for the prompt.
3. Build agent.py - takes NL question, includes schema in the prompt, generates SQL, returns it.
4. Build sql_validator.py - runs BQ dry-run on the SQL; if syntax errors, feeds the error back to Gemini for a retry (max 2 retries).
5. Build summarizer.py - takes the SQL result table and writes a 2–3 sentence NL summary.
6. Build chart_picker.py - picks an appropriate chart type (bar, line, pie, scatter) based on the result shape.
7. Write 15 test queries spanning easy (single-table aggregation), medium (joins), hard (window functions).
8. Run all 15, log SQL + result + summary + chart pick.

Deliverable:-
1) /text2sql/ project: agent.py, schema_loader.py, sql_validator.py, summarizer.py, chart_picker.py
2) /text2sql/dataset_choice.md - your chosen dataset + key tables + why
3) /text2sql/test_queries.md - 15 NL queries grouped by difficulty
4) /text2sql/test_results/ - one folder per query: nl_question, generated_sql, validation_status, result_table.csv, nl_summary, chart.png, success/failure
5) /text2sql/learnings.md: schema-prompting tricks that worked, hallucinated-column failures, how validation caught bad SQL, accuracy by difficulty bucket

Reference:-
cloud.google.com/bigquery/public-data

## Day 7 GOAL 3: Document everything you've learned about RAG into a single decision matrix the team can actually use in client conversations.

WHAT TO PRODUCE: A 1-page document that helps anyone at Wohlig pick the right RAG pattern for a new client scenario. This is the kind of doc Bilal might use in a pre-sales meeting.

STEPS:
1. Build a matrix table - 5 rows (RAG patterns: naive, hybrid, contextual, text2SQL, agentic), 7 columns (data type, query type, citation need, scale, accuracy ceiling, cost, complexity).
2. Build a second table - 5 rows (client scenarios: insurance claim assist, retail BI dashboard chatbot, HR FAQ, medical knowledge bot, sales call intel), each mapped to a recommended pattern with 1-line reasoning.
3. Add a simple decision flowchart (in Mermaid or as a hand-drawn screenshot): 'What does the user query look like?' → recommended RAG pattern.
4. Add 3 sentences on when to combine patterns (e.g. text2SQL + RAG for hybrid BI).

Deliverable:-
/strategy/rag_decision_matrix.md (1 page, client-pitch-ready) containing:
1) Matrix table - 5 RAG patterns × 7 evaluation columns
2) Scenario table - 5 Wohlig-style scenarios mapped to recommended pattern + reasoning
3) Decision flowchart (mermaid or image)
4) 3 sentences on stacking patterns

# Day 8

## Day 8 GOAL 1: Build a production-quality MCP server - the modern way to give agents access to enterprise systems.

MCP - Connecting Agents to Enterprise Systems

Task:-
CONCEPT: MCP (Model Context Protocol) is a standard for how LLMs talk to external tools. You write an MCP server once (in Python), and ANY MCP-compatible client (Gemini, Claude, Cursor, etc.) can use it. This is exactly the pattern we use for Wohlig clients who need agents to access internal systems.

BUILD A SERVER WITH 4 TOOLS:
• query_bigquery(sql) - but with safety: read-only check, cost limit (reject queries that would scan > 100MB based on dry-run)
• list_gcs_objects(bucket, prefix) - list files in GCS
• read_gcs_object(bucket, path) - read a file (with a size limit to prevent loading huge files)
• send_slack_message(channel, message) - STUBBED (just prints, doesn't actually send)

STEPS:
1. Install the MCP Python SDK. Read the quickstart.
2. Write server.py and tools/ folder (one file per tool).
3. For each tool: define input schema using JSON schema, validate inputs, return structured error responses if something fails.
4. Add safety checks (read-only SQL parser, cost dry-run check, file size check).
5. Write pytest tests: happy path for each tool, validation failure, safety-limit hit.

Deliverable:-
1) /mcp_server/ project: server.py, tools/ folder (one file per tool)
2) /mcp_server/safety/ - query cost-limit checker, GCS size limit, Slack rate limit
3) /mcp_server/tests/ - pytest cases per tool: happy path, validation failure, downstream failure, safety-limit hit
4) /mcp_server/README.md - tool catalogue with input/output schemas + example calls
5) /mcp_server/error_format.md - the structured error response format for future MCP servers

Reference:-
modelcontextprotocol.io/quickstart/server

## Day 8 GOAL 2: Deploy your MCP server to Cloud Run so it can be used remotely - and add real production essentials (auth, logging, rate limits).

MCP - Connecting Agents to Enterprise Systems

Task:-
CONCEPT: Running a server locally is fine for testing. For client work it needs to be deployed somewhere reachable, protected by auth (API key minimum), and observable (logs + traces).

STEPS:
1. Write a multi-stage Dockerfile.
2. Write auth middleware: every request must include x-api-key header; reject if missing or wrong.
3. Write rate-limit middleware: max 60 requests/minute per API key.
4. Add Cloud Logging integration - every tool call logs as a structured log entry (tool name, args, duration, status).
5. Write deploy.sh - runs `gcloud run deploy` with all the right flags (region, memory, env vars).
6. Deploy. Get the live URL.
7. Hit the deployed URL with 5 test calls. Take screenshots of the Cloud Trace and Cloud Logging entries.

Deliverable:-
1) /mcp_server/Dockerfile - multi-stage build
2) /mcp_server/deploy.sh - gcloud command with full flags
3) /mcp_server/middleware/ - auth.py, rate_limit.py, logging.py
4) /mcp_deploy/cloud_run_url.txt - live URL
5) /mcp_deploy/trace_ids.md - 5 example calls with timestamp, tool called, input, output, trace ID + screenshots from Cloud Console
6) /mcp_deploy/auth_setup.md - how a new client gets/rotates an API key

Reference:-
cloud.google.com/run/docs

## Day 8 GOAL 3: Verify your MCP server works with multiple MCP clients - because the value of MCP is the same server works everywhere.

MCP - Connecting Agents to Enterprise Systems

Task:-
STEPS:
1. Connect your deployed MCP server to Gemini via ADK's MCPToolset (Python config).
2. Connect the same MCP server to Claude Code (edit ~/.claude.json to add your server URL + API key).
3. Pick 3 test queries: (a) single-tool ('List files in bucket X'), (b) multi-tool ('List files in X, then read the first one'), (c) error case (e.g. malformed SQL - to see how each client surfaces errors).
4. Run all 3 from both clients. Compare behavior side-by-side.
5. Document any differences (tool-call format, error display, auth handling) and whether any server-side changes would help compatibility.

Deliverable:-
/mcp_clients/client_comparison.md containing:
1) Setup steps for both clients with exact config files
2) The 3 test queries
3) Side-by-side table: query, gemini_behavior, claude_behavior, differences observed
4) Notes on auth/format/error differences
5) Recommendation: any server-side changes to improve cross-client compatibility

Reference:-
modelcontextprotocol.io


# Day 9

## Day 9 GOAL 1: Build your first ADK agent that combines built-in tools and your custom MCP server.

ADK Multi-Agent (BI Co-Pilot / Doc Governance Pattern)

Task:-
CONCEPT: ADK (Agent Development Kit) is Google's framework for building agents. It handles the boring parts (state, sessions, tool routing, eval) so you focus on the logic. An ADK agent can have multiple tool sources - built-in tools like google_search, custom Python tools, AND MCP servers.

STEPS:
1. Install ADK (pip install google-adk). Walk through the Get Started.
2. Write agent.py - an LlmAgent with:
   a) google_search built-in tool
   b) Your Day-8 MCP server connected via MCPToolset
3. Add a before_tool_callback that logs every tool call to Cloud Logging with: agent_name, tool_called, args, trace_id, timestamp.
4. Run the agent in ADK Dev UI (`adk web`).
5. Test with 5 queries that need both tool sources (e.g. 'Find the top 5 cloud providers on Google, then check our BigQuery to see which ones we have data for').
6. Screenshot Cloud Logging filtered to your agent.

Deliverable:-
1) /adk_agent/ project with agent.py
2) /adk_agent/callbacks.py - before_tool_callback that logs structured entries
3) /adk_agent/test_queries.md - 5 queries exercising both tool sources
4) /adk_agent/cloud_logging_screenshot.png - Cloud Logging showing the structured logs
5) /adk_agent/test_results.md - 5 conversations end-to-end with tool-call traces

Reference:-
adk.dev/docs/get-started

## Day 9 GOAL 2: Build a multi-agent BI co-pilot - the same pattern as the Jindal Leadership Co-Pilot.

ADK Multi-Agent (BI Co-Pilot / Doc Governance Pattern)

Task:-
CONCEPT: One big agent that does everything is hard to debug and fails often. The standard pattern: a small orchestrator decides which specialist sub-agent handles each query, then aggregates the results.

ARCHITECTURE:
• structured-data-agent - answers questions that need BigQuery data (uses your Day-7 text2SQL agent or similar)
• unstructured-data-agent - answers questions that need policy/PDF data (uses your Day-6 RAG bot)
• orchestrator - looks at the user's question, picks one or both sub-agents, runs them, combines results into one final answer

STEPS:
1. Build the 2 sub-agents as ADK LlmAgents (or reuse logic from earlier days).
2. Build the orchestrator as a parent LlmAgent with the 2 sub-agents in its sub_agents list. Write its instruction prompt carefully - it should describe what each sub-agent is good at.
3. Draw an architecture diagram showing the agent topology.
4. Write 10 test queries: 3 BQ-only, 3 RAG-only, 4 needing both.
5. Run all 10. Save which sub-agents got called for each, in what order, and the final answer.
6. Note any routing failures (orchestrator picked the wrong sub-agent) and fix the orchestrator prompt.

Deliverable:-
1) /bi_copilot/ project: orchestrator.py, agents/structured.py, agents/unstructured.py, prompts/
2) /bi_copilot/architecture.md - diagram + agent topology + delegation logic
3) /bi_copilot/test_queries.md - 10 queries categorized
4) /bi_copilot/test_results/ - for each query: which sub-agents called, intermediate outputs, final answer, was routing correct (YES/NO + reasoning)
5) /bi_copilot/routing_failures.md - any cases where orchestrator picked wrong agent + how you fixed the prompt

Reference:-
adk.dev/docs/agents/multi-agent

## Day 9 GOAL 3:  Use ADK's evaluation framework to verify your BI co-pilot actually works - and to debug when it doesn't.

ADK Multi-Agent (BI Co-Pilot / Doc Governance Pattern)

Task:-
CONCEPT: ADK has a built-in eval framework. You write test cases in JSON, define metrics, run them, and ADK gives you a report. It also lets you 'rewind' to any step of a failing case in the Dev UI for debugging.

STEPS:
1. Write evalset.json - 10 ADK eval cases. Each case has: query, expected_tool_calls (which sub-agents should be invoked), reference_response (the ideal answer).
2. Write 2 custom metrics:
   a) cites_sources (boolean) - does the response contain at least 1 citation in the expected format?
   b) response_grounded (LLM-judge, 0–1) - Gemini judges if the answer is actually grounded in the retrieved/queried data
3. Run the eval with `adk eval`. Save the HTML report.
4. Pick 2 failed cases. Open them in the Dev UI. Walk through each step to find the root cause (e.g. orchestrator skipped a sub-agent, sub-agent retrieved no chunks, prompt was off).
5. Document the failures + your proposed fixes.


Deliverable:-
1) /bi_copilot/evalset.json - 10 eval cases
2) /bi_copilot/custom_metrics.py - cites_sources + response_grounded
3) /bi_copilot/eval_run_report.html - ADK-generated report
4) /bi_copilot/failure_analysis.md - 2 failures with Dev UI screenshots, root cause, proposed fix

Reference:-
adk.dev/docs/evaluate


# Day 10

## Day 10 GOAL 1: Get hands-on with Gemini Enterprise's no-code Agent Designer - Wohlig pitches this to clients who want fast results without engineering.

Gemini Enterprise + Deployment + Mini-Capstone

Task:-
CONCEPT: Gemini Enterprise is Google's enterprise AI platform. Agent Designer is a no-code UI inside it where business users can build agents - write instructions, attach data via connectors (Drive, SharePoint), add tools. Compare this with the ADK code-based approach.

STEPS:
1. Get access to a Gemini Enterprise sandbox tenant.
2. Create 20 sample HR documents (leave policy, expense rules, onboarding guide, etc.) - generate them with Gemini if you don't have real ones. Upload to Google Drive.
3. In Gemini Enterprise, create a new data store using the Drive connector.
4. In Agent Designer, build a new agent: write Goal, Instructions, attach the data store, add Examples, configure Output format.
5. Test with 10 HR questions. Note which were answered well, partially, wrong, or hallucinated.
6. Publish the agent to Agent Gallery so others can use it.
7. Document everything with screenshots (10+).
8. Write a short comparison: which client scenarios suit no-code Agent Designer vs ADK code agents.

Deliverable:-
1) /ge_agent/walkthrough.md - step-by-step build guide with 10+ screenshots
2) /ge_agent/sample_hr_docs/ - the 20 HR docs you indexed
3) /ge_agent/test_results.md - 10 test questions + responses + accuracy verdict
4) /ge_agent/ge_agent_url.txt - live agent URL
5) /ge_agent/no_code_vs_adk.md - short comparison: which scenarios suit each

Reference:-
cloud.google.com/gemini-enterprise


## Day 10 GOAL 2: Deploy your Day-9 BI co-pilot to production - both Vertex AI Agent Engine and Cloud Run - and figure out the trade-offs.

Gemini Enterprise + Deployment + Mini-Capstone

Task:-
CONCEPT: Gemini Enterprise is Google's enterprise AI platform. Agent Designer is a no-code UI inside it where business users can build agents - write instructions, attach data via connectors (Drive, SharePoint), add tools. Compare this with the ADK code-based approach.

STEPS:
1CONCEPT: Two main ways to deploy an agent in production:
• Vertex AI Agent Engine - managed runtime for agents. Handles sessions, scaling, tracing. Higher abstraction,         less control.
• Cloud Run - generic container service. More control, more setup, but the ops team already knows it.

Wohlig clients ask which to pick all the time. You need a clear opinion.
STEPS:
1. Deploy your Day-9 BI co-pilot to Vertex AI Agent Engine.
2. Wire up Cloud Trace + Cloud Logging. Run a 5-turn conversation. Take screenshots of the trace showing every sub-agent call and tool call.
3. Containerize the same agent (Dockerfile). Deploy to Cloud Run.
4. Run the same 5-turn conversation. Capture traces.
5. Write a comparison: managed sessions? scaling model? cost per request? cold start? observability? dev velocity? Make a clear recommendation for 4 client situations: (a) PoC, (b) low-traffic prod, (c) high-traffic prod, (d) regulated/compliance-heavy client.

Deliverable:-
1) /deploy/agent_engine/ - deployment scripts, env config
2) /deploy/cloud_run/ - Dockerfile, deploy.sh
3) /deploy/endpoints.md - both live URLs + curl examples
4) /deploy/trace_screenshots/ - Cloud Trace screenshots for a 5-turn conversation on each platform
5) /deploy/agent_engine_vs_run.md (1 page): comparison table + recommendations for 4 client situations

Reference:-
cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview


## Day 10 GOAL 3: Mini-capstone - pick ONE Wohlig client pattern and ship it end-to-end.

Gemini Enterprise + Deployment + Mini-Capstone

Task:-
PICK ONE:
(a) BI Co-Pilot over a public BigQuery dataset (e.g. NYC taxi, e-commerce) - Jindal pattern
(b) Creative Generation Agent (image + video for a fictional brand) - Croma/HDFC pattern
(c) Document Governance + RAG bot over a public corpus - Meesho Memory pattern
(d) Voice/Chat Customer-Service Agent over MCP - Apollo/Meesho voice bot pattern

STEPS:
1. Pick one (start your day with this decision).
2. Spend 30 min on a quick design - what's the architecture, what tools you'll use, what success looks like.
3. Build it end-to-end - reuse everything you built across the last 9 days.
4. Deploy publicly (Cloud Run or Agent Engine).
5. Build a small eval (5–10 cases) showing it works.
6. Write a 1-page architecture doc in Wohlig format.
7. Record a 5-min Loom: problem → demo → architecture → what would change for a real client.
8. Write a 'next steps' note - if this went to a real client, what would you build next?

Deliverable:-
1) /capstone/ project - full source with README
2) /capstone/deployed_url.txt - publicly accessible URL
3) /capstone/architecture.md (1 page, Wohlig format): problem, chosen pattern, architecture diagram, key decisions, tech stack, cost/1000-requests estimate
4) /capstone/loom_link.txt - 5-min walkthrough video
5) /capstone/eval_results.csv - small eval (5–10 cases) showing it works
6) /capstone/next_steps.md - 3 things you'd build next if this went to a real client

