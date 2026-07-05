# AI Engineer — 10 Tasks (Beginner → 2‑Year Experience)

> **Goal:** Go from "I've heard of AI" to "I can build intelligent applications that use LLMs, APIs, embeddings, and tool‑calling."
> An AI Engineer bridges the gap between ML research and production software — you integrate AI models into real applications.
> Each task is self‑contained. Difficulty increases from Task 1 → 10.

---

## Task 1: Understand LLMs — Architecture, Tokenisation & How They Actually Work

**Difficulty:** ⭐ Beginner

**What you'll learn:**
- What a Large Language Model is (Transformer architecture at a high level)
- Tokenisation — how text becomes numbers
- Temperature, top‑k, top‑p — what they control
- Context window and token limits

**What to read first:**
- 📖 [3Blue1Brown: But what is a GPT?](https://www.youtube.com/watch?v=wjZofJX0v4M) (video, 27 min)
- 📖 [Jay Alammar: The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- 📖 [OpenAI Tokenizer Tool](https://platform.openai.com/tokenizer) (interactive)
- 📖 [Hugging Face: What is a Tokenizer?](https://huggingface.co/docs/transformers/tokenizer_summary)

**Task:**
1. Write `tokenizer_explore.py` that:
   - Takes 10 different text inputs (short sentence, long paragraph, code snippet, emoji, Hindi text, JSON, URL, etc.)
   - Uses `tiktoken` (OpenAI's tokenizer) or Hugging Face tokenizer to tokenize each
   - Prints: input text, token count, tokens (as strings), token IDs
   - Calculates the cost to process each input at $0.50 per 1M input tokens
2. Write `temperature_experiment.py` that:
   - Uses any free LLM API (Groq, Ollama, or Hugging Face Inference API)
   - Sends the same prompt 5 times at temperatures: 0.0, 0.3, 0.7, 1.0, 1.5
   - Saves all 25 outputs
   - Analyses: at temp=0, are outputs identical? At temp=1.5, how creative/random are they?
3. Write `llm_basics.md`:
   - Explain in your own words: What is a token? Why does tokenisation matter for cost and context window?
   - What does temperature do? When would you set it to 0 vs 1?

**Deliverables:**
1. `/ai_engineer/task1/tokenizer_explore.py`
2. `/ai_engineer/task1/temperature_experiment.py`
3. `/ai_engineer/task1/llm_basics.md` — your explanations
4. `/ai_engineer/task1/temperature_outputs/` — 25 saved outputs

---

## Task 2: Prompt Engineering — From Zero‑Shot to Chain‑of‑Thought

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- Zero‑shot, Few‑shot, and Role‑based prompting
- System prompts vs user prompts
- Chain‑of‑Thought (CoT) prompting
- Structured output from LLMs (JSON mode)

**What to read first:**
- 📖 [Prompt Engineering Guide](https://www.promptingguide.ai/) (read: Zero‑Shot, Few‑Shot, CoT sections)
- 📖 [OpenAI: Prompt Engineering Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- 📖 [Anthropic: Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

**Task:**
1. Pick a classification task: categorise 20 customer support emails into 6 categories (Billing, Technical, Account, Shipping, Returns, General).
2. Write 4 prompt variants:
   - `zero_shot.txt` — just describe the categories, no examples
   - `few_shot.txt` — include 3 example email→category pairs
   - `role_based.txt` — "You are a senior support specialist at…"
   - `cot.txt` — "Read the email. Think step by step about what the customer needs. Then classify."
3. Write `evaluate_prompts.py` that:
   - Runs all 20 emails through each prompt variant using a free LLM
   - Compares predictions to your manually‑labelled ground truth
   - Computes accuracy per prompt style
4. Try getting the LLM to return **structured JSON** (e.g., `{"category": "Billing", "confidence": "high", "reasoning": "..."}`). Note which models support this well.
5. Write `prompt_comparison.md` — accuracy table, examples of where each style won/failed, your rule of thumb.

**Deliverables:**
1. `/ai_engineer/task2/prompts/` — 4 prompt files
2. `/ai_engineer/task2/evaluate_prompts.py`
3. `/ai_engineer/task2/results.csv` — email_id, ground_truth, zero_shot_pred, few_shot_pred, role_pred, cot_pred
4. `/ai_engineer/task2/prompt_comparison.md`

---

## Task 3: Building with LLM APIs — Chat Interface & Conversation Memory

**Difficulty:** ⭐⭐ Beginner+

**What you'll learn:**
- Making API calls to an LLM (request/response format)
- Multi‑turn conversation: maintaining chat history
- System prompts to set behaviour
- Handling streaming responses

**What to read first:**
- 📖 [Groq API Docs](https://console.groq.com/docs/quickstart) (free, fast, Llama models)
- 📖 [Ollama: Run LLMs Locally](https://ollama.com/) (alternative — no API key needed)
- 📖 [Gradio Quickstart](https://www.gradio.app/guides/quickstart) (for building UI)

**Task:**
1. Write `chatbot.py` — a terminal chatbot that:
   - Uses Groq API (free) or Ollama (local) to call an LLM
   - Maintains conversation history (appends each user message + assistant reply to a list)
   - Has a system prompt: "You are a helpful coding tutor. Explain concepts simply. Use analogies."
   - Supports commands: `/clear` (reset history), `/history` (show full conversation), `/exit`
   - Handles errors gracefully (API timeout, rate limit)
2. Write `chatbot_gradio.py` — wrap the same logic in a Gradio `ChatInterface` so you have a web UI.
3. Test with a 10‑turn conversation where you ask follow‑up questions (to test memory works).
4. Write `conversation_design.md`:
   - How does the LLM "remember" previous messages? (hint: it doesn't — you send the full history each time)
   - What happens when the conversation exceeds the context window? How would you handle it?

**Deliverables:**
1. `/ai_engineer/task3/chatbot.py` — terminal version
2. `/ai_engineer/task3/chatbot_gradio.py` — web UI version
3. `/ai_engineer/task3/sample_conversation.md` — 10‑turn conversation transcript
4. `/ai_engineer/task3/conversation_design.md` — memory management explanation

---

## Task 4: Structured Data Extraction — Turning Documents into JSON

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Using LLMs to extract structured data from unstructured text
- Pydantic models for output validation
- Handling extraction failures and retries
- Real‑world use case: invoice/receipt/form processing

**What to read first:**
- 📖 [Pydantic Docs](https://docs.pydantic.dev/latest/) (Models section)
- 📖 [Instructor Library](https://python.useinstructor.com/) (structured output from LLMs)
- 📖 [OpenAI: JSON Mode](https://platform.openai.com/docs/guides/structured-outputs)

**Task:**
1. Pick a document type: job postings, product listings, or restaurant menus.
2. Create or find 10 unstructured text samples (e.g., paste 10 job postings from LinkedIn).
3. Define a Pydantic schema for the extracted data:
   ```python
   class JobPosting(BaseModel):
       title: str
       company: str
       location: str
       salary_range: Optional[str]
       experience_years: Optional[int]
       skills: list[str]
       remote: bool
   ```
4. Write `extract.py` that:
   - Takes a text input
   - Calls an LLM with a prompt asking it to extract data into your schema
   - Validates the response against your Pydantic model
   - If validation fails, retries up to 3 times with the error message appended to the prompt
5. Run on all 10 samples. Manually check each extraction.
6. Write `extraction_report.md`:
   - Accuracy per field (e.g., "title was correct 10/10, salary was correct 6/10")
   - Common failure patterns and how to fix them

**Deliverables:**
1. `/ai_engineer/task4/extract.py`
2. `/ai_engineer/task4/schema.py` — Pydantic model
3. `/ai_engineer/task4/samples/` — 10 text inputs
4. `/ai_engineer/task4/extractions/` — 10 JSON outputs
5. `/ai_engineer/task4/extraction_report.md`

---

## Task 5: Function Calling — Giving LLMs the Ability to Use Tools

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- Function calling / tool use — how LLMs invoke external functions
- Defining tool schemas (JSON Schema)
- The agent loop: LLM → tool call → execute → return result → LLM responds
- When to use function calling vs just prompting

**What to read first:**
- 📖 [OpenAI: Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- 📖 [Groq: Tool Use](https://console.groq.com/docs/tool-use) (free)
- 📖 [LangChain: Tools & Agents](https://python.langchain.com/docs/how_to/#tools) (reference)

**Task:**
1. Build a **personal assistant agent** with 4 tools:
   - `get_weather(city)` — returns fake weather data from a JSON file
   - `calculate(expression)` — evaluates a math expression safely using `ast.literal_eval`
   - `search_notes(query)` — searches a local folder of text files and returns matching snippets
   - `create_reminder(text, time)` — saves a reminder to a JSON file
2. Write `agent.py` that:
   - Sends the user message + tool definitions to the LLM
   - If the LLM wants to call a tool: parse the tool call, execute it, send the result back
   - Loop until the LLM gives a final text response
   - Handle errors: invalid tool call, tool execution failure
3. Test with 10 queries:
   - 3 single‑tool ("What's the weather in Mumbai?")
   - 3 multi‑tool ("What's the weather in Delhi and remind me to carry an umbrella if it's rainy")
   - 2 no‑tool ("Tell me a joke")
   - 2 error cases (invalid city, impossible math)
4. Log every tool call: tool_name, args, result, time_taken.

**Deliverables:**
1. `/ai_engineer/task5/agent.py`
2. `/ai_engineer/task5/tools.py` — 4 tool implementations
3. `/ai_engineer/task5/tool_definitions.json` — JSON schema for each tool
4. `/ai_engineer/task5/test_results.md` — 10 queries with tool calls logged
5. `/ai_engineer/task5/agent_loop_explained.md` — diagram of the agent loop

---

## Task 6: Embeddings & Semantic Search — Finding Meaning, Not Keywords

**Difficulty:** ⭐⭐⭐ Intermediate

**What you'll learn:**
- What embeddings are (dense vector representations of text)
- How semantic search works (cosine similarity)
- Building a simple search engine without any vector database
- Embedding models: sentence‑transformers (free, local)

**What to read first:**
- 📖 [Sentence Transformers Docs](https://www.sbert.net/docs/quickstart.html) (free, local models)
- 📖 [Jay Alammar: Illustrated Word2Vec](https://jalammar.github.io/illustrated-word2vec/)
- 📖 [Pinecone: What are Vector Embeddings?](https://www.pinecone.io/learn/vector-embeddings/) (blog)

**Task:**
1. Collect 100+ text items: use Wikipedia paragraphs, news articles, or your own notes. Save as `corpus.jsonl` (one JSON object per line: `{"id": 1, "text": "..."}`).
2. Write `embed.py` that:
   - Loads a free embedding model locally: `sentence-transformers/all-MiniLM-L6-v2`
   - Embeds all 100 items → saves as `embeddings.npy` (numpy array)
   - Saves the index mapping: `index.json` (id → position in the array)
3. Write `search.py` that:
   - Takes a natural language query
   - Embeds the query using the same model
   - Computes cosine similarity against all corpus embeddings
   - Returns top‑5 most similar items with scores
4. Test with 10 queries. Include 2 queries where the exact words don't appear in any document but the meaning matches (to prove semantic search works).
5. Write `semantic_search_notes.md`:
   - How is this different from keyword search (like `grep`)?
   - What are the limitations? When does it fail?

**Deliverables:**
1. `/ai_engineer/task6/embed.py`
2. `/ai_engineer/task6/search.py`
3. `/ai_engineer/task6/corpus.jsonl` — 100+ items
4. `/ai_engineer/task6/search_results.md` — 10 queries with top‑5 results
5. `/ai_engineer/task6/semantic_search_notes.md`

---

## Task 7: RAG (Retrieval‑Augmented Generation) — Build a Q&A Bot Over Your Own Documents

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- The RAG pattern: Retrieve → Augment → Generate
- Chunking documents into searchable pieces
- Grounding LLM answers in retrieved context
- Preventing hallucination with careful prompting

**What to read first:**
- 📖 [LangChain: RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/) (free)
- 📖 [Pinecone: What is RAG?](https://www.pinecone.io/learn/retrieval-augmented-generation/) (blog)
- 📖 [Anthropic: Contextual Retrieval](https://www.anthropic.com/research/contextual-retrieval)

**Task:**
1. Collect 10–20 PDF or text documents on one topic (e.g., Python documentation, cooking recipes, a textbook chapter).
2. Write `ingest.py` that:
   - Reads all documents
   - Chunks each into ~500‑word segments (sentence‑aware — don't split mid‑sentence)
   - Embeds each chunk using sentence‑transformers
   - Saves chunks + embeddings + metadata (doc_name, chunk_id, page)
3. Write `rag_bot.py` that:
   - Takes a user question
   - Retrieves top‑5 relevant chunks (semantic search)
   - Builds a prompt: "Answer the question using ONLY the context below. Cite your sources as [doc_name:chunk_id]. If the context doesn't contain the answer, say 'I don't have this information.'"
   - Calls the LLM and returns the grounded answer
4. Wrap in a Gradio UI.
5. Test with 5 questions that SHOULD have answers + 3 questions that should NOT. Verify the bot says "I don't know" for the latter.

**Deliverables:**
1. `/ai_engineer/task7/ingest.py`
2. `/ai_engineer/task7/rag_bot.py` + `rag_gradio.py`
3. `/ai_engineer/task7/system_prompt.txt` — the grounding prompt
4. `/ai_engineer/task7/test_results.md` — 8 queries with responses, citations, and pass/fail
5. `/ai_engineer/task7/rag_architecture.md` — diagram + explanation of the pipeline

---

## Task 8: Evaluating AI Systems — LLM‑as‑Judge & Automated Testing

**Difficulty:** ⭐⭐⭐⭐ Intermediate+

**What you'll learn:**
- Why you can't just "vibe check" AI outputs
- LLM‑as‑Judge: using one LLM to evaluate another's output
- Key metrics: faithfulness, relevance, groundedness
- Building an automated eval harness

**What to read first:**
- 📖 [Hamel Husain: Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/) (essential blog)
- 📖 [Braintrust: Introduction to Evals](https://www.braintrust.dev/docs/guides/evals)
- 📖 [RAGAS Docs](https://docs.ragas.io/) (RAG evaluation framework)

**Task:**
1. Take your RAG bot from Task 7 (or build a simple one).
2. Create `test_set.jsonl` — 20 question-answer pairs with:
   - `question`: the user's question
   - `ground_truth_answer`: what the correct answer should be
   - `ground_truth_chunks`: which chunks should be retrieved
3. Write 3 judge prompts (each in its own file):
   - `judge_faithfulness.txt` — "Is the answer supported by the provided context? Score 0‑1."
   - `judge_relevance.txt` — "Does the answer address the question? Score 0‑1."
   - `judge_groundedness.txt` — "Does every claim in the answer have a citation? Score 0‑1."
4. Write `run_eval.py` that:
   - Runs all 20 questions through your RAG bot
   - For each answer, runs all 3 judges (using a different LLM call)
   - Saves results to `eval_results.csv`
5. Write `eval_report.md`:
   - Aggregate scores per metric
   - Top 3 best answers, bottom 3 worst answers, with root‑cause analysis
   - What would you improve based on the eval?

**Deliverables:**
1. `/ai_engineer/task8/test_set.jsonl`
2. `/ai_engineer/task8/judge_prompts/` — 3 judge prompt files
3. `/ai_engineer/task8/run_eval.py`
4. `/ai_engineer/task8/eval_results.csv`
5. `/ai_engineer/task8/eval_report.md`

---

## Task 9: Multi‑Agent Systems — Orchestrating Specialised AI Agents

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Why one big agent fails — the case for specialised sub‑agents
- Orchestrator pattern: a "manager" agent delegates to specialists
- Agent communication: passing context between agents
- Error handling in multi‑agent systems

**What to read first:**
- 📖 [Google ADK: Multi‑Agent](https://google.github.io/adk-docs/agents/multi-agents/) (if using ADK)
- 📖 [LangGraph: Multi‑Agent Architectures](https://langchain-ai.github.io/langgraph/concepts/multi_agent/) (alternative)
- 📖 [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (essential read)

**Task:**
1. Build a **research assistant** with 3 agents:
   - `search_agent` — searches a local corpus or uses a web search API
   - `summarizer_agent` — takes search results and produces a concise summary
   - `fact_checker_agent` — takes claims from the summary and verifies them against the search results
   - `orchestrator` — receives the user's question, coordinates the 3 agents
2. Flow:
   - User asks a question → Orchestrator calls search_agent → gets results
   - Orchestrator calls summarizer_agent with results → gets summary
   - Orchestrator calls fact_checker_agent with summary + original results → gets fact‑check report
   - Orchestrator combines and returns final answer
3. Test with 5 questions. Log which agents were called, in what order, and what each returned.
4. Introduce a failure: make search_agent return empty results for 2 queries. How does the system handle it?

**Deliverables:**
1. `/ai_engineer/task9/orchestrator.py`
2. `/ai_engineer/task9/agents/` — search_agent.py, summarizer_agent.py, fact_checker_agent.py
3. `/ai_engineer/task9/test_results.md` — 5 queries with full agent traces
4. `/ai_engineer/task9/failure_handling.md` — how the system behaved on empty results
5. `/ai_engineer/task9/multi_agent_architecture.md` — diagram + design decisions

---

## Task 10: Production AI Application — End‑to‑End Deployment

**Difficulty:** ⭐⭐⭐⭐⭐ Advanced

**What you'll learn:**
- Packaging an AI application for deployment
- Rate limiting, error handling, and logging in production
- Cost estimation and optimisation
- Monitoring AI applications in production

**What to read first:**
- 📖 [FastAPI + Docker](https://fastapi.tiangolo.com/deployment/docker/)
- 📖 [LiteLLM: Unified LLM API](https://docs.litellm.ai/) (switch models easily)
- 📖 [Langfuse: LLM Observability](https://langfuse.com/docs) (free, open‑source)

**Task:**
1. Take your best project from Tasks 1–9 (RAG bot or multi‑agent system).
2. Wrap it in a FastAPI application with:
   - `POST /chat` — main endpoint, accepts question, returns answer
   - `GET /health` — health check
   - Rate limiting: max 10 requests/minute per IP
   - Request logging: every request logs input, output, latency, tokens used, model called
   - Error handling: graceful failures with user‑friendly error messages
3. Write a `Dockerfile` and `docker-compose.yml`.
4. Add cost tracking:
   - For each request, estimate the cost (input tokens × price + output tokens × price)
   - Log cumulative costs to a `costs.csv`
5. Write `production_checklist.md`:
   - Security: API key auth, input sanitisation, PII handling
   - Monitoring: what to track, alerting on high error rate
   - Scaling: when to add caching, when to switch models
   - Cost optimisation: cheaper models for simple queries, caching frequent answers

**Deliverables:**
1. `/ai_engineer/task10/app.py` — FastAPI application
2. `/ai_engineer/task10/Dockerfile` + `docker-compose.yml`
3. `/ai_engineer/task10/production_checklist.md`
4. `/ai_engineer/task10/cost_tracker.py` — cost estimation per request
5. `/ai_engineer/task10/monitoring_notes.md` — what to monitor and why

---

## Learning Path Summary

| Task | Topic | Difficulty | Key Tools |
|------|-------|-----------|-----------|
| 1 | LLM Fundamentals — Tokens, Temperature | ⭐ | tiktoken, Groq/Ollama |
| 2 | Prompt Engineering | ⭐⭐ | Free LLM API |
| 3 | Chat Interface & Memory | ⭐⭐ | Groq, Gradio |
| 4 | Structured Extraction | ⭐⭐⭐ | Pydantic, Instructor |
| 5 | Function Calling / Tool Use | ⭐⭐⭐ | Groq/Ollama |
| 6 | Embeddings & Semantic Search | ⭐⭐⭐ | sentence‑transformers |
| 7 | RAG — Q&A over Documents | ⭐⭐⭐⭐ | sentence‑transformers, Gradio |
| 8 | AI Evaluation (LLM‑as‑Judge) | ⭐⭐⭐⭐ | RAGAS / custom judges |
| 9 | Multi‑Agent Systems | ⭐⭐⭐⭐⭐ | Custom / LangGraph / ADK |
| 10 | Production Deployment | ⭐⭐⭐⭐⭐ | FastAPI, Docker |

**All tools are free and open‑source. No paid cloud services required.**
