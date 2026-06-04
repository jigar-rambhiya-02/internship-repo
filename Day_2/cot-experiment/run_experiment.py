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
INITIAL_BACKOFF_SECONDS = 5

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
    "scenario_id", "customer_name", "policy_type",
    "claim_description", "policy_rules", "ground_truth", "reasoning_hint"
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
            time.sleep(2)

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