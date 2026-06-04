# Chain-of-Thought (CoT) Prompting Experiment — Complete Guide

> **Who this is for:** A Gen AI intern who wants to go beyond "just calling an API" and understand *when* and *why* CoT prompting actually moves the needle — and when it wastes your money.

---

## Table of Contents

1. [What You're Building & Why](#1-what-youre-building--why)
2. [Folder Structure](#2-folder-structure)
3. [Copy-Paste Prompts for DeepSeek Chat](#3-copy-paste-prompts-for-deepseek-chat)
4. [Example Scenarios](#4-example-scenarios)
5. [Complete Python Script](#5-complete-python-script)
6. [Instructions to Run](#6-instructions-to-run)
7. [Expected Output & Accuracy Table](#7-expected-output--accuracy-table)
8. [Troubleshooting](#8-troubleshooting)
9. [learnings.md Template](#9-learningsmd-template)

---

## 1. What You're Building & Why

You are running a **controlled experiment** comparing three prompting strategies on 15 insurance claim scenarios that have clear Yes/No ground-truth answers. This gives you measurable signal, not vibes.

| Strategy | What It Does | When to Use |
|---|---|---|
| **Direct** | Ask for Yes/No immediately | Simple, low-stakes, cost-sensitive |
| **CoT** | Force step-by-step reasoning before answering | Complex rules, multi-condition logic |
| **Self-Consistency (SC)** | Run CoT 5× at high temperature, take majority vote | High-stakes decisions where accuracy > cost |

**The honest goal:** By the end you should be able to answer "Is CoT worth the 3–5× token cost for this specific task?" with data, not guesswork.

---

## 2. Folder Structure

```
cot-experiment/
│
├── .env                        # Groq API key (never commit this)
├── .gitignore                  # Ignores .env, __pycache__, results
├── requirements.txt            # Python dependencies
├── run_experiment.py           # Main experiment script (the big one)
│
├── cot/
│   ├── scenarios.jsonl         # 15 insurance claim scenarios (one JSON per line)
│   │
│   ├── prompts/
│   │   ├── direct.txt          # Direct prompting template
│   │   ├── cot.txt             # Chain-of-Thought prompting template
│   │   └── sc.txt              # Self-consistency prompt template
│   │
│   └── results.csv             # Auto-generated after running the experiment
│
└── learnings.md                # Your observations (fill in after running)
```

**Why this structure?**

- Prompts live in `.txt` files, not hardcoded in Python. This means you can iterate on prompts without touching code — a critical habit.
- `scenarios.jsonl` uses one JSON object per line (JSONL format), which is streaming-friendly and easy to extend.
- Results go to CSV so you can analyze them in Excel, Pandas, or any BI tool without touching the script again.

---

## 3. Copy-Paste Prompts for DeepSeek Chat

Use these prompts to generate each required file. Open DeepSeek Chat, paste the prompt, copy the output, and save it to the correct file path.

---

### 3.1 Generate `cot/scenarios.jsonl`

---

📋 **COPY THIS PROMPT**

```
Generate exactly 15 insurance claim scenarios for a Chain-of-Thought prompting experiment. Each scenario must have a clear, unambiguous Yes/No ground-truth answer for claim approval.

Output ONLY valid JSONL — one JSON object per line, no extra text, no markdown fences, no numbering.

Each object must have EXACTLY these fields:
- "scenario_id": string like "S01", "S02", ... "S15"
- "policy_holder_name": realistic full name (string)
- "policy_details": object with fields:
    - "policy_type": one of ["health", "auto", "home", "life", "travel"]
    - "coverage_amount_usd": integer
    - "deductible_usd": integer
    - "premium_per_month_usd": integer
    - "policy_start_date": "YYYY-MM-DD"
    - "policy_end_date": "YYYY-MM-DD"
    - "exclusions": list of strings
- "claim_details": object with fields:
    - "claim_date": "YYYY-MM-DD"
    - "claim_amount_usd": integer
    - "claim_type": string
    - "description": string (2-3 sentences)
- "applicable_rules": list of strings (2-4 rules that are relevant to this claim)
- "ground_truth": "Yes" or "No" (string, claim approved or denied)
- "correct_answer_reasoning": string (2-3 sentences explaining why ground_truth is correct)

Mix of approvals and denials. Include edge cases like:
- Claim filed before policy start
- Claim type explicitly listed in exclusions
- Claim amount under deductible
- Policy lapsed before claim date
- Valid claims that clearly should be approved
- Pre-existing condition exclusion (health policies)
- Claims filed after policy expiry

Aim for roughly 8 approvals and 7 denials to avoid label imbalance.
```

---

### 3.2 Generate `cot/prompts/direct.txt`

---

📋 **COPY THIS PROMPT**

```
Write a direct prompting template for an insurance claim approval decision system. The template will be used as a Python format string, so use {scenario_json} as the single placeholder where the scenario JSON will be injected.

Rules:
- Be concise. Do not ask the model to think out loud or explain.
- Instruct the model to respond with ONLY "Yes" or "No" (no punctuation, no explanation).
- Include a brief one-line system-level framing about what the model is.
- The prompt should work when {scenario_json} is replaced with a raw JSON string of the scenario.

Output ONLY the prompt text. No explanation, no markdown fences, no preamble.
```

---

### 3.3 Generate `cot/prompts/cot.txt`

---

📋 **COPY THIS PROMPT**

```
Write a Chain-of-Thought (CoT) prompting template for an insurance claim approval decision system. The template will be used as a Python format string, so use {scenario_json} as the single placeholder where the scenario JSON will be injected.

Rules:
- Instruct the model to reason step by step BEFORE giving the final answer.
- The reasoning steps should explicitly address: (1) policy validity at claim date, (2) whether the claim type is covered or excluded, (3) whether the claim amount exceeds the deductible, (4) any other applicable rules.
- After the reasoning, the model must output the final answer on its own line in this exact format: "Final Answer: Yes" or "Final Answer: No"
- The prompt should work when {scenario_json} is replaced with a raw JSON string of the scenario.

Output ONLY the prompt text. No explanation, no markdown fences, no preamble.
```

---

### 3.4 Generate `cot/prompts/sc.txt`

---

📋 **COPY THIS PROMPT**

```
Write a self-consistency prompting template for an insurance claim approval decision system. This template is used for a single reasoning pass — the script will call this prompt 5 times at temperature=0.7 and take a majority vote.

The template will be used as a Python format string, so use {scenario_json} as the single placeholder.

Rules:
- This is structurally identical to a CoT prompt, but add a brief instruction that the model should reason independently, as if seeing this scenario for the first time.
- After reasoning, the model must output: "Final Answer: Yes" or "Final Answer: No" on its own line.
- Do NOT mention voting, multiple runs, or temperature in the prompt itself.
- The prompt should work when {scenario_json} is replaced with a raw JSON string of the scenario.

Output ONLY the prompt text. No explanation, no markdown fences, no preamble.
```

---

## 4. Example Scenarios

Here are two full example scenarios showing the exact JSONL format you should produce. Use these to verify the output from DeepSeek looks correct before running the experiment.

**Scenario 1 — Should be APPROVED (Yes)**

```json
{"scenario_id": "S01", "policy_holder_name": "Priya Nair", "policy_details": {"policy_type": "health", "coverage_amount_usd": 100000, "deductible_usd": 500, "premium_per_month_usd": 180, "policy_start_date": "2023-01-01", "policy_end_date": "2025-12-31", "exclusions": ["cosmetic surgery", "dental", "vision correction"]}, "claim_details": {"claim_date": "2024-07-15", "claim_amount_usd": 8200, "claim_type": "emergency hospitalization", "description": "Priya was admitted for an acute appendicitis requiring emergency surgery. She was hospitalized for 3 days and discharged with full recovery."}, "applicable_rules": ["Claim must be filed during active policy period", "Emergency hospitalization is covered under standard health policy", "Claim amount must exceed deductible for reimbursement", "Covered services must not appear in the exclusions list"], "ground_truth": "Yes", "correct_answer_reasoning": "The policy was active on the claim date (2024-07-15 is within 2023-01-01 to 2025-12-31). Emergency hospitalization is not in the exclusions list. The claim amount of $8,200 far exceeds the $500 deductible, so the net payable amount is $7,700."}
```

**Scenario 2 — Should be DENIED (No)**

```json
{"scenario_id": "S02", "policy_holder_name": "Marcus Webb", "policy_details": {"policy_type": "auto", "coverage_amount_usd": 25000, "deductible_usd": 1000, "premium_per_month_usd": 95, "policy_start_date": "2024-03-01", "policy_end_date": "2025-02-28", "exclusions": ["racing events", "off-road driving", "driving under influence"]}, "claim_details": {"claim_date": "2024-11-20", "claim_amount_usd": 4500, "claim_type": "collision damage during off-road event", "description": "Marcus filed a claim for front-end collision damage sustained while participating in an off-road trail event. The damage occurred on an unpaved mountain trail outside city limits."}, "applicable_rules": ["Policy covers collision damage on public roads only", "Off-road driving is explicitly excluded from coverage", "Claims must be filed within 30 days of incident", "Excluded events are not eligible for any reimbursement regardless of damage amount"], "ground_truth": "No", "correct_answer_reasoning": "The claim is for damage sustained during off-road driving, which is explicitly listed in the policy exclusions. Excluded events are not eligible for reimbursement regardless of claim amount or deductible. The claim must be denied."}
```

---

## 5. Complete Python Script

Save this as `run_experiment.py` in the project root.

```python
"""
Chain-of-Thought Prompting Experiment
Domain: Insurance Claim Approval
Model: openai/gpt-oss-120b via Groq API
Error handling: STRICT — fail loudly, no silent failures
"""

import os
import json
import time
import logging
import csv
from datetime import datetime
from collections import Counter
from pathlib import Path
from typing import Optional

from groq import Groq, APIStatusError, APIConnectionError, APITimeoutError
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

MODEL = "openai/gpt-oss-120b"
SCENARIOS_PATH = Path("cot/scenarios.jsonl")
RESULTS_PATH = Path("cot/results.csv")
PROMPTS_DIR = Path("cot/prompts")

# Groq pricing (USD per 1M tokens) — update if Groq changes pricing
INPUT_COST_PER_M = 0.15
OUTPUT_COST_PER_M = 0.60

# Self-consistency settings
SC_RUNS = 5
SC_TEMPERATURE = 0.7

# Retry settings for 429 rate limits
MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 2

# ─────────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("experiment.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# SETUP & VALIDATION
# ─────────────────────────────────────────────

def load_environment() -> str:
    """Load and validate the Groq API key from environment. Fails loudly if missing."""
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "FATAL: GROQ_API_KEY environment variable is not set.\n"
            "Fix: Create a .env file in the project root with:\n"
            "  GROQ_API_KEY=your_key_here\n"
            "Or set it directly: export GROQ_API_KEY=your_key_here"
        )
    if not api_key.startswith("gsk_"):
        raise EnvironmentError(
            f"FATAL: GROQ_API_KEY looks malformed (expected to start with 'gsk_').\n"
            f"Got: {api_key[:10]}...\n"
            "Fix: Get a valid key from https://console.groq.com"
        )
    logger.info("API key validated.")
    return api_key


def load_scenarios() -> list[dict]:
    """Load and validate all scenarios from JSONL. Fails loudly on parse errors."""
    if not SCENARIOS_PATH.exists():
        raise FileNotFoundError(
            f"FATAL: Scenarios file not found at '{SCENARIOS_PATH}'.\n"
            "Fix: Generate it using the DeepSeek prompt in guide.md Section 3.1,\n"
            f"then save it to '{SCENARIOS_PATH}'."
        )

    scenarios = []
    required_keys = {
        "scenario_id", "policy_holder_name", "policy_details",
        "claim_details", "applicable_rules", "ground_truth", "correct_answer_reasoning"
    }

    with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                scenario = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"FATAL: JSON parse error on line {line_num} of '{SCENARIOS_PATH}'.\n"
                    f"Error: {e}\n"
                    f"Content: {line[:120]}...\n"
                    "Fix: Validate your JSONL at https://jsonlint.com (paste one line at a time)."
                ) from e

            missing = required_keys - set(scenario.keys())
            if missing:
                raise ValueError(
                    f"FATAL: Scenario on line {line_num} is missing required fields: {missing}\n"
                    f"scenario_id: {scenario.get('scenario_id', 'UNKNOWN')}\n"
                    "Fix: Regenerate the scenario using the DeepSeek prompt in guide.md."
                )

            if scenario["ground_truth"] not in ("Yes", "No"):
                raise ValueError(
                    f"FATAL: ground_truth must be exactly 'Yes' or 'No' (case-sensitive).\n"
                    f"Got: '{scenario['ground_truth']}' in scenario {scenario.get('scenario_id')}\n"
                    "Fix: Edit the JSONL file and correct the ground_truth value."
                )

            scenarios.append(scenario)

    if len(scenarios) == 0:
        raise ValueError(
            f"FATAL: No scenarios found in '{SCENARIOS_PATH}'.\n"
            "Fix: The file exists but is empty. Regenerate using the DeepSeek prompt."
        )

    logger.info(f"Loaded {len(scenarios)} scenarios from '{SCENARIOS_PATH}'.")
    return scenarios


def load_prompt_template(strategy: str) -> str:
    """Load a prompt template file. Fails loudly if missing."""
    path = PROMPTS_DIR / f"{strategy}.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"FATAL: Prompt template not found at '{path}'.\n"
            f"Fix: Generate it using the DeepSeek prompt in guide.md Section 3 for '{strategy}',\n"
            f"then save it to '{path}'."
        )
    template = path.read_text(encoding="utf-8").strip()
    if "{scenario_json}" not in template:
        raise ValueError(
            f"FATAL: Prompt template '{path}' does not contain the required placeholder '{{scenario_json}}'.\n"
            "Fix: Regenerate the prompt template — it must include {{scenario_json}} exactly once."
        )
    logger.info(f"Loaded prompt template: '{path}'.")
    return template


# ─────────────────────────────────────────────
# COST TRACKING
# ─────────────────────────────────────────────

def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate USD cost from token counts using configured pricing."""
    input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_M
    output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_M
    return round(input_cost + output_cost, 8)


# ─────────────────────────────────────────────
# API CALL WITH RETRY
# ─────────────────────────────────────────────

def call_groq_with_retry(
    client: Groq,
    prompt: str,
    temperature: float = 0.0,
    scenario_id: str = "UNKNOWN",
    attempt_label: str = "",
) -> tuple[str, int, int]:
    """
    Call Groq API with exponential backoff retry on 429 rate limits.

    Returns:
        (response_text, input_tokens, output_tokens)

    Raises:
        RuntimeError if all retries are exhausted or a non-retryable error occurs.
    """
    backoff = INITIAL_BACKOFF_SECONDS

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                f"[{scenario_id}]{attempt_label} API call attempt {attempt}/{MAX_RETRIES} "
                f"(temp={temperature})"
            )
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=1024,
            )

            # Validate response structure before accessing fields
            if not response.choices:
                raise RuntimeError(
                    f"FATAL: Groq API returned an empty 'choices' list for scenario '{scenario_id}'.\n"
                    "This is unexpected. Check if the model is available and your prompt is valid."
                )

            message = response.choices[0].message
            if message is None or message.content is None:
                raise RuntimeError(
                    f"FATAL: Groq API returned a null message content for scenario '{scenario_id}'.\n"
                    f"Response object: {response}\n"
                    "This may indicate a content policy refusal or a model error."
                )

            content = message.content.strip()

            # Validate usage block exists for cost tracking
            if response.usage is None:
                logger.warning(
                    f"[{scenario_id}] Usage data missing from response. Defaulting token counts to 0."
                )
                input_tokens, output_tokens = 0, 0
            else:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens

            return content, input_tokens, output_tokens

        except APIStatusError as e:
            if e.status_code == 429:
                if attempt == MAX_RETRIES:
                    raise RuntimeError(
                        f"FATAL: Groq rate limit (429) hit {MAX_RETRIES} times for scenario '{scenario_id}'.\n"
                        f"Last error: {e}\n"
                        "Fix: Wait a few minutes and re-run, or reduce the number of concurrent requests.\n"
                        "Groq free tier has strict RPM (requests per minute) limits."
                    ) from e
                logger.warning(
                    f"[{scenario_id}] Rate limit hit (429). "
                    f"Retrying in {backoff}s (attempt {attempt}/{MAX_RETRIES})..."
                )
                time.sleep(backoff)
                backoff *= 2  # Exponential backoff
            elif e.status_code == 401:
                raise RuntimeError(
                    "FATAL: Groq API returned 401 Unauthorized.\n"
                    "Fix: Your GROQ_API_KEY is invalid or expired.\n"
                    "Get a new key at https://console.groq.com"
                ) from e
            elif e.status_code == 404:
                raise RuntimeError(
                    f"FATAL: Groq API returned 404 — model '{MODEL}' not found.\n"
                    "Fix: Check the model name at https://console.groq.com/docs/models\n"
                    "The model may have been deprecated or the name may have changed."
                ) from e
            else:
                raise RuntimeError(
                    f"FATAL: Groq API error (status {e.status_code}) for scenario '{scenario_id}'.\n"
                    f"Error: {e}\n"
                    "This is not a rate limit — do not retry automatically."
                ) from e

        except APIConnectionError as e:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"FATAL: Could not connect to Groq API after {MAX_RETRIES} attempts.\n"
                    f"Last error: {e}\n"
                    "Fix: Check your internet connection. Groq endpoint: api.groq.com"
                ) from e
            logger.warning(f"[{scenario_id}] Connection error. Retrying in {backoff}s...")
            time.sleep(backoff)
            backoff *= 2

        except APITimeoutError as e:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"FATAL: Groq API timed out after {MAX_RETRIES} attempts for scenario '{scenario_id}'.\n"
                    f"Last error: {e}\n"
                    "Fix: The model may be overloaded. Wait and retry."
                ) from e
            logger.warning(f"[{scenario_id}] Timeout. Retrying in {backoff}s...")
            time.sleep(backoff)
            backoff *= 2


# ─────────────────────────────────────────────
# ANSWER PARSING
# ─────────────────────────────────────────────

def parse_direct_answer(raw: str, scenario_id: str) -> str:
    """
    Extract Yes/No from a direct prompt response.
    Expected: response is just "Yes" or "No".
    """
    cleaned = raw.strip().rstrip(".").capitalize()
    if cleaned in ("Yes", "No"):
        return cleaned

    # Fallback: look for Yes/No anywhere in the response
    upper = raw.upper()
    if "YES" in upper and "NO" not in upper:
        logger.warning(
            f"[{scenario_id}] Direct answer fuzzy-matched to 'Yes'. Raw: '{raw[:80]}'"
        )
        return "Yes"
    if "NO" in upper and "YES" not in upper:
        logger.warning(
            f"[{scenario_id}] Direct answer fuzzy-matched to 'No'. Raw: '{raw[:80]}'"
        )
        return "No"

    logger.error(
        f"[{scenario_id}] Could not parse direct answer from: '{raw[:200]}'\n"
        "Defaulting to 'PARSE_ERROR'. This scenario will count as incorrect."
    )
    return "PARSE_ERROR"


def parse_cot_answer(raw: str, scenario_id: str) -> str:
    """
    Extract Yes/No from a CoT response.
    Expected format: response ends with a line like "Final Answer: Yes" or "Final Answer: No"
    """
    lines = raw.strip().splitlines()
    for line in reversed(lines):
        line_clean = line.strip()
        if line_clean.lower().startswith("final answer:"):
            answer_part = line_clean.split(":", 1)[1].strip().rstrip(".").capitalize()
            if answer_part in ("Yes", "No"):
                return answer_part
            logger.warning(
                f"[{scenario_id}] 'Final Answer:' line found but value is not Yes/No: '{answer_part}'"
            )

    # Fallback: check last line for bare Yes/No
    if lines:
        last = lines[-1].strip().rstrip(".").capitalize()
        if last in ("Yes", "No"):
            logger.warning(
                f"[{scenario_id}] CoT 'Final Answer:' format not found. "
                f"Fell back to last line: '{last}'"
            )
            return last

    logger.error(
        f"[{scenario_id}] Could not parse CoT answer. Raw (last 300 chars): '{raw[-300:]}'\n"
        "Defaulting to 'PARSE_ERROR'."
    )
    return "PARSE_ERROR"


def majority_vote(answers: list[str], scenario_id: str) -> str:
    """
    Take majority vote from a list of Yes/No answers.
    Ties go to 'No' (conservative default for insurance).
    """
    valid = [a for a in answers if a in ("Yes", "No")]
    if not valid:
        logger.error(
            f"[{scenario_id}] No valid answers in SC run. All {len(answers)} answers failed to parse.\n"
            "Defaulting to 'PARSE_ERROR'."
        )
        return "PARSE_ERROR"

    if len(valid) < len(answers):
        logger.warning(
            f"[{scenario_id}] {len(answers) - len(valid)} SC run(s) failed to parse. "
            f"Voting on {len(valid)} valid answers."
        )

    counts = Counter(valid)
    logger.info(
        f"[{scenario_id}] SC vote — Yes: {counts.get('Yes', 0)}, No: {counts.get('No', 0)}"
    )

    if counts.get("Yes", 0) > counts.get("No", 0):
        return "Yes"
    return "No"  # Tie-breaking defaults to No (conservative)


# ─────────────────────────────────────────────
# STRATEGY RUNNERS
# ─────────────────────────────────────────────

def run_direct(
    client: Groq, scenario: dict, template: str
) -> tuple[str, float]:
    """Run direct prompting strategy. Returns (answer, cost_usd)."""
    scenario_id = scenario["scenario_id"]
    prompt = template.format(scenario_json=json.dumps(scenario, indent=2))
    raw, in_tok, out_tok = call_groq_with_retry(
        client, prompt, temperature=0.0, scenario_id=scenario_id, attempt_label=" [DIRECT]"
    )
    answer = parse_direct_answer(raw, scenario_id)
    cost = calculate_cost(in_tok, out_tok)
    logger.info(f"[{scenario_id}] DIRECT → {answer} | Cost: ${cost:.6f}")
    return answer, cost


def run_cot(
    client: Groq, scenario: dict, template: str
) -> tuple[str, float]:
    """Run Chain-of-Thought prompting strategy. Returns (answer, cost_usd)."""
    scenario_id = scenario["scenario_id"]
    prompt = template.format(scenario_json=json.dumps(scenario, indent=2))
    raw, in_tok, out_tok = call_groq_with_retry(
        client, prompt, temperature=0.0, scenario_id=scenario_id, attempt_label=" [COT]"
    )
    answer = parse_cot_answer(raw, scenario_id)
    cost = calculate_cost(in_tok, out_tok)
    logger.info(f"[{scenario_id}] COT → {answer} | Cost: ${cost:.6f}")
    return answer, cost


def run_self_consistency(
    client: Groq, scenario: dict, template: str
) -> tuple[str, float]:
    """
    Run self-consistency: SC_RUNS calls at SC_TEMPERATURE, take majority vote.
    Returns (answer, total_cost_usd).
    """
    scenario_id = scenario["scenario_id"]
    prompt = template.format(scenario_json=json.dumps(scenario, indent=2))
    answers = []
    total_cost = 0.0

    for run_idx in range(1, SC_RUNS + 1):
        raw, in_tok, out_tok = call_groq_with_retry(
            client,
            prompt,
            temperature=SC_TEMPERATURE,
            scenario_id=scenario_id,
            attempt_label=f" [SC run {run_idx}/{SC_RUNS}]",
        )
        parsed = parse_cot_answer(raw, scenario_id)
        answers.append(parsed)
        total_cost += calculate_cost(in_tok, out_tok)
        # Small sleep between SC runs to avoid burst rate limits
        if run_idx < SC_RUNS:
            time.sleep(0.5)

    final_answer = majority_vote(answers, scenario_id)
    logger.info(
        f"[{scenario_id}] SC → {final_answer} | Total cost: ${total_cost:.6f}"
    )
    return final_answer, total_cost


# ─────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────

def save_results(results: list[dict]) -> None:
    """Write results to CSV. Overwrites any existing file."""
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "scenario_id",
        "ground_truth",
        "direct_answer",
        "direct_correct",
        "cot_answer",
        "cot_correct",
        "sc_answer",
        "sc_correct",
        "direct_cost_usd",
        "cot_cost_usd",
        "sc_cost_usd",
    ]
    with open(RESULTS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    logger.info(f"Results saved to '{RESULTS_PATH}'.")


def print_summary(results: list[dict]) -> None:
    """Print accuracy and cost summary to stdout."""
    total = len(results)
    if total == 0:
        logger.warning("No results to summarize.")
        return

    def accuracy(key: str) -> str:
        correct = sum(1 for r in results if r[key] == "True")
        return f"{correct}/{total} ({correct/total*100:.1f}%)"

    def total_cost(key: str) -> str:
        cost = sum(float(r[key]) for r in results)
        return f"${cost:.6f}"

    print("\n" + "=" * 55)
    print("  EXPERIMENT SUMMARY")
    print("=" * 55)
    print(f"  Scenarios run:        {total}")
    print(f"  Model:                {MODEL}")
    print(f"  SC runs per scenario: {SC_RUNS}")
    print()
    print(f"  {'Strategy':<18} {'Accuracy':<20} {'Total Cost'}")
    print(f"  {'-'*50}")
    print(f"  {'Direct':<18} {accuracy('direct_correct'):<20} {total_cost('direct_cost_usd')}")
    print(f"  {'CoT':<18} {accuracy('cot_correct'):<20} {total_cost('cot_cost_usd')}")
    print(f"  {'Self-Consistency':<18} {accuracy('sc_correct'):<20} {total_cost('sc_cost_usd')}")
    print("=" * 55)
    print(f"\nFull results: {RESULTS_PATH}")
    print(f"Full logs:    experiment.log\n")


# ─────────────────────────────────────────────
# MAIN EXPERIMENT RUNNER
# ─────────────────────────────────────────────

def run_experiment() -> None:
    """
    Main experiment entry point.
    Runs all three strategies on all scenarios and saves results to CSV.
    """
    start_time = datetime.now()
    logger.info(f"{'='*55}")
    logger.info(f"Experiment started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Model: {MODEL}")
    logger.info(f"{'='*55}")

    # --- Setup ---
    api_key = load_environment()
    client = Groq(api_key=api_key)
    scenarios = load_scenarios()

    direct_template = load_prompt_template("direct")
    cot_template = load_prompt_template("cot")
    sc_template = load_prompt_template("sc")

    results = []

    # --- Run all scenarios ---
    for i, scenario in enumerate(scenarios, start=1):
        scenario_id = scenario["scenario_id"]
        ground_truth = scenario["ground_truth"]
        logger.info(
            f"\n[{i}/{len(scenarios)}] Processing scenario: {scenario_id} "
            f"| Ground truth: {ground_truth}"
        )

        row = {
            "scenario_id": scenario_id,
            "ground_truth": ground_truth,
        }

        # Direct
        direct_answer, direct_cost = run_direct(client, scenario, direct_template)
        row["direct_answer"] = direct_answer
        row["direct_correct"] = str(direct_answer == ground_truth)
        row["direct_cost_usd"] = direct_cost

        # CoT
        cot_answer, cot_cost = run_cot(client, scenario, cot_template)
        row["cot_answer"] = cot_answer
        row["cot_correct"] = str(cot_answer == ground_truth)
        row["cot_cost_usd"] = cot_cost

        # Self-Consistency
        sc_answer, sc_cost = run_self_consistency(client, scenario, sc_template)
        row["sc_answer"] = sc_answer
        row["sc_correct"] = str(sc_answer == ground_truth)
        row["sc_cost_usd"] = sc_cost

        results.append(row)

        # Save after each scenario (so a crash mid-run doesn't lose all data)
        save_results(results)

    # --- Final summary ---
    elapsed = datetime.now() - start_time
    logger.info(
        f"\nExperiment complete. Total time: {elapsed.total_seconds():.1f}s"
    )
    print_summary(results)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    run_experiment()
```

---

## 6. Instructions to Run

### Step 1 — Get a Groq API Key

1. Go to [https://console.groq.com](https://console.groq.com) and sign up or log in.
2. Navigate to **API Keys** and create a new key.
3. Copy it — you won't see it again.

### Step 2 — Set Up the Project

```bash
# Clone or create the project folder
mkdir cot-experiment && cd cot-experiment

# Create the folder structure
mkdir -p cot/prompts

# Create .gitignore BEFORE adding any keys
cat > .gitignore << 'EOF'
.env
__pycache__/
*.pyc
experiment.log
EOF
```

### Step 3 — Create `.env` File

```bash
# Create .env with your Groq API key
echo "GROQ_API_KEY=gsk_your_actual_key_here" > .env
```

**Never commit `.env` to git.** The `.gitignore` above handles this.

### Step 4 — Install Dependencies

```bash
pip install groq pandas python-dotenv
```

Or if you prefer a `requirements.txt`:

```bash
# Create requirements.txt
cat > requirements.txt << 'EOF'
groq>=0.9.0
pandas>=2.0.0
python-dotenv>=1.0.0
EOF

pip install -r requirements.txt
```

### Step 5 — Generate and Save the Required Files

Using the DeepSeek prompts from Section 3:

1. Paste the **Section 3.1 prompt** into DeepSeek → save output to `cot/scenarios.jsonl`
2. Paste the **Section 3.2 prompt** into DeepSeek → save output to `cot/prompts/direct.txt`
3. Paste the **Section 3.3 prompt** into DeepSeek → save output to `cot/prompts/cot.txt`
4. Paste the **Section 3.4 prompt** into DeepSeek → save output to `cot/prompts/sc.txt`

**Verify your JSONL before running:**

```bash
# Each line should be valid JSON — this will print an error if any line is broken
python -c "
import json
with open('cot/scenarios.jsonl') as f:
    for i, line in enumerate(f, 1):
        if line.strip():
            json.loads(line)  # Will throw if invalid
            print(f'Line {i}: OK')
print('All scenarios valid.')
"
```

### Step 6 — Save the Python Script

Save the full script from Section 5 as `run_experiment.py` in the project root.

### Step 7 — Run the Experiment

```bash
python run_experiment.py
```

You will see live logging in the terminal. The script saves `cot/results.csv` after each scenario, so if it crashes, you won't lose completed work. Logs are also written to `experiment.log`.

### Step 8 — Interpreting Output

**Terminal summary (printed at end):**

```
=======================================================
  EXPERIMENT SUMMARY
=======================================================
  Scenarios run:        15
  Model:                openai/gpt-oss-120b
  SC runs per scenario: 5

  Strategy           Accuracy             Total Cost
  --------------------------------------------------
  Direct             12/15 (80.0%)        $0.000420
  CoT                14/15 (93.3%)        $0.001850
  Self-Consistency   15/15 (100.0%)       $0.009200
=======================================================
```

**`cot/results.csv` columns:**

| Column | What It Means |
|---|---|
| `scenario_id` | Scenario identifier (S01–S15) |
| `ground_truth` | The correct answer (Yes/No) |
| `direct_answer` | What the direct strategy answered |
| `direct_correct` | True/False — did it match ground_truth? |
| `cot_answer` | What CoT answered |
| `cot_correct` | True/False |
| `sc_answer` | Majority vote across 5 SC runs |
| `sc_correct` | True/False |
| `direct_cost_usd` | API cost in USD for this scenario (direct) |
| `cot_cost_usd` | API cost for CoT on this scenario |
| `sc_cost_usd` | Total API cost across all 5 SC runs |

**Quick analysis in Python:**

```python
import pandas as pd

df = pd.read_csv("cot/results.csv")

# Accuracy per strategy
print(df[["direct_correct","cot_correct","sc_correct"]].apply(
    lambda col: (col == "True").mean()
))

# Where CoT helped but Direct failed
helped = df[(df["direct_correct"] == "False") & (df["cot_correct"] == "True")]
print(f"\nCoT fixed {len(helped)} scenarios that Direct got wrong:")
print(helped[["scenario_id","ground_truth","direct_answer","cot_answer"]])

# Cost comparison
print(f"\nAvg cost per scenario:")
print(df[["direct_cost_usd","cot_cost_usd","sc_cost_usd"]].mean())
```

---

## 7. Expected Output / Accuracy Table

Fill this in after running the experiment. Replace all `???` values with your actual results.

```
Model: openai/gpt-oss-120b
Date run: YYYY-MM-DD
Total scenarios: 15
SC runs: 5 × temperature=0.7
```

| Scenario ID | Ground Truth | Direct | Direct ✓ | CoT | CoT ✓ | SC | SC ✓ |
|---|---|---|---|---|---|---|---|
| S01 | Yes | ??? | ??? | ??? | ??? | ??? | ??? |
| S02 | No | ??? | ??? | ??? | ??? | ??? | ??? |
| S03 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| S04 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| S05 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| S06 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| S07 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| S08 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| S09 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| S10 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| S11 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| S12 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| S13 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| S14 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| S15 | ??? | ??? | ??? | ??? | ??? | ??? | ??? |
| **TOTAL** | — | — | **??/15** | — | **??/15** | — | **??/15** |

**Cost Summary:**

| Strategy | Total Cost (USD) | Avg per Scenario | Relative Cost |
|---|---|---|---|
| Direct | $??? | $??? | 1× |
| CoT | $??? | $??? | ??× |
| Self-Consistency | $??? | $??? | ??× |

---

## 8. Troubleshooting

### 429 Rate Limit Errors

**Symptom:** `APIStatusError: 429 Too Many Requests` in logs.

**Groq-specific context:** Groq free tier enforces both RPM (requests per minute) and TPM (tokens per minute) limits. The self-consistency strategy makes 5 consecutive API calls per scenario, which can easily hit RPM limits mid-run.

**Fixes:**
- The script already implements exponential backoff (doubles wait time each retry, up to 5 retries).
- If you're still hitting limits, increase `INITIAL_BACKOFF_SECONDS = 2` to `5` or `10` at the top of the script.
- Increase the `time.sleep(0.5)` between SC runs to `time.sleep(2)`.
- Check your current rate limits at [https://console.groq.com/settings/limits](https://console.groq.com/settings/limits).

---

### 401 Invalid API Key

**Symptom:** `RuntimeError: FATAL: Groq API returned 401 Unauthorized.`

**Fixes:**
- Verify your `.env` file exists in the project root (same folder as `run_experiment.py`).
- Verify the key starts with `gsk_` and has no trailing whitespace.
- Regenerate the key at [https://console.groq.com](https://console.groq.com) if needed.

```bash
# Check your .env file looks right (this reveals the key — don't share output)
cat .env
```

---

### 404 Model Not Found

**Symptom:** `RuntimeError: FATAL: Groq API returned 404 — model 'openai/gpt-oss-120b' not found.`

**Fixes:**
- The model `openai/gpt-oss-120b` may have been deprecated or renamed.
- Check current available models:

```python
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
models = client.models.list()
for m in models.data:
    print(m.id)
```

- Update `MODEL = "openai/gpt-oss-120b"` at the top of `run_experiment.py` with the correct model ID.

---

### JSON Parsing Errors in `scenarios.jsonl`

**Symptom:** `ValueError: FATAL: JSON parse error on line X of 'cot/scenarios.jsonl'`

**Fixes:**
- DeepSeek sometimes wraps output in markdown fences (` ```json ` ... ` ``` `). Strip those out.
- Open the file and look at the exact line number mentioned in the error.
- Paste that line into [https://jsonlint.com](https://jsonlint.com) to find the exact syntax error.
- Common issues: trailing commas, single quotes instead of double quotes, unescaped newlines in strings.

---

### `PARSE_ERROR` in Results CSV

**Symptom:** `direct_answer` or `cot_answer` column shows `PARSE_ERROR` instead of Yes/No.

**What this means:** The model's response did not follow the expected format. The script logged a warning or error with the raw response — check `experiment.log`.

**Fixes:**
- Open `experiment.log` and search for `PARSE_ERROR` to find the raw response.
- The most common cause: your CoT prompt template doesn't instruct the model to output `Final Answer: Yes/No` on its own line, or the model ignored the instruction.
- Iterate on your prompt template in `cot/prompts/cot.txt` and re-run.

---

### Empty Responses

**Symptom:** `RuntimeError: FATAL: Groq API returned a null message content.`

**Fixes:**
- This typically means the model triggered a content policy refusal. Insurance claim scenarios are generally safe, but if any scenario description includes unusual phrasing, it might trigger filters.
- Try rephrasing the problematic scenario in `cot/scenarios.jsonl`.
- Check if the same scenario fails consistently — if so, it's a prompt issue, not a transient error.

---

## 9. `learnings.md` Template

Save this as `learnings.md` in the project root after completing the experiment.

```markdown
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
```

---

*Guide version 1.0 — built for the Groq API with model `openai/gpt-oss-120b`.*
*If the model changes, update the `MODEL` constant in `run_experiment.py` and verify the token cost rates still apply.*
