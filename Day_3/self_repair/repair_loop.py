# repair_loop.py
# Calls Groq to extract a ContactCard from messy text.
# Validates with Pydantic. If invalid, sends a repair prompt.
# Retries up to max_retries times (default 3 total attempts).

import json
import os
import re
from typing import Optional

from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError

from schema import ContactCard

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"

# Groq pricing estimate (check console.groq.com for latest rates)
# These are approximate — update if you find official per-token costs for this model
COST_PER_1K_INPUT_TOKENS = 0.0006   # USD per 1K input tokens
COST_PER_1K_OUTPUT_TOKENS = 0.0006  # USD per 1K output tokens

CONTACT_CARD_SCHEMA = {
    "name": "string — full name of the person",
    "email": "string — valid email address",
    "phone": "string — 10-digit Indian mobile number (may include country code, dashes, spaces — you must normalize)",
    "address": {
        "city": "string — name of the city",
        "pincode": "string — exactly 6 digits"
    }
}

EXTRACTION_SYSTEM_PROMPT = """You are a data extraction assistant. Your job is to extract contact information from messy real-world text.

You MUST respond with ONLY a valid JSON object. No explanations, no markdown code fences, no extra text — just the raw JSON.

The JSON must match this exact schema:
{schema}

Rules:
- name: Extract the full name. Correct obvious OCR errors (e.g. "Rahui" → "Rahul").
- email: Extract the email. Correct obvious OCR errors (e.g. "gmai1.com" → "gmail.com", "rahul@gmall" → "rahul@gmail.com").
- phone: Extract the phone number as a string. Include digits only (you may keep the raw form — the validator will normalize it).
- address.city: Extract the city name.
- address.pincode: Extract exactly 6 digits. Do not add or remove digits.

If a field is completely absent and cannot be inferred, use an empty string "" — do not omit the key.
""".format(schema=json.dumps(CONTACT_CARD_SCHEMA, indent=2))

REPAIR_SYSTEM_PROMPT = """You are a data extraction repair assistant. A previous attempt to extract contact information failed validation.

Your job is to fix the JSON so it passes the schema validation.

You MUST respond with ONLY a valid JSON object. No explanations, no markdown, no extra text.

The required schema is:
{schema}
""".format(schema=json.dumps(CONTACT_CARD_SCHEMA, indent=2))


def strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` fences if the model adds them."""
    text = text.strip()
    # Remove opening fence
    text = re.sub(r"^```(?:json)?\s*", "", text)
    # Remove closing fence
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def call_groq(messages: list[dict]) -> tuple[str, dict]:
    """Call the Groq API and return (response_text, usage_dict)."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.0,
        max_tokens=512,
    )
    text = response.choices[0].message.content or ""
    usage = {
        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
    }
    return text, usage


def estimate_cost(total_input_tokens: int, total_output_tokens: int) -> float:
    """Estimate USD cost from token counts."""
    input_cost = (total_input_tokens / 1000) * COST_PER_1K_INPUT_TOKENS
    output_cost = (total_output_tokens / 1000) * COST_PER_1K_OUTPUT_TOKENS
    return round(input_cost + output_cost, 6)


def run_repair_loop(
    raw_input: str,
    max_retries: int = 3
) -> dict:
    """
    Extract a ContactCard from raw_input with self-repair on validation failure.

    Returns a dict with:
        parsed          : ContactCard | None
        first_try_valid : bool
        final_valid     : bool
        num_retries     : int   (number of repair attempts after first try)
        errors_seen     : list[str]
        total_input_tokens  : int
        total_output_tokens : int
        estimated_cost  : float (USD)
    """
    errors_seen = []
    total_input_tokens = 0
    total_output_tokens = 0
    first_try_valid = False
    parsed = None

    # ── First attempt ──────────────────────────────────────────────────────────
    messages = [
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": f"Extract the contact card from this text:\n\n{raw_input}"},
    ]

    raw_output, usage = call_groq(messages)
    total_input_tokens += usage["prompt_tokens"]
    total_output_tokens += usage["completion_tokens"]

    cleaned = strip_markdown_fences(raw_output)

    try:
        data = json.loads(cleaned)
        parsed = ContactCard(**data)
        first_try_valid = True
        return {
            "parsed": parsed,
            "first_try_valid": True,
            "final_valid": True,
            "num_retries": 0,
            "errors_seen": [],
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "estimated_cost": estimate_cost(total_input_tokens, total_output_tokens),
        }
    except (json.JSONDecodeError, ValidationError, Exception) as e:
        error_msg = str(e)
        errors_seen.append(f"Attempt 1: {error_msg}")

    # ── Repair loop ────────────────────────────────────────────────────────────
    previous_output = raw_output  # raw (may include fences) for context

    for attempt in range(2, max_retries + 2):  # attempts 2, 3, 4 (if max_retries=3)
        repair_user_content = (
            f"The original input text was:\n\n{raw_input}\n\n"
            f"The previous model output was:\n\n{previous_output}\n\n"
            f"This output failed validation with the following error:\n{errors_seen[-1]}\n\n"
            f"Please extract the contact card again, fixing the validation error. "
            f"Return ONLY valid JSON matching the schema. No extra text, no markdown fences."
        )

        repair_messages = [
            {"role": "system", "content": REPAIR_SYSTEM_PROMPT},
            {"role": "user", "content": repair_user_content},
        ]

        raw_output, usage = call_groq(repair_messages)
        total_input_tokens += usage["prompt_tokens"]
        total_output_tokens += usage["completion_tokens"]
        previous_output = raw_output
        cleaned = strip_markdown_fences(raw_output)

        try:
            data = json.loads(cleaned)
            parsed = ContactCard(**data)
            return {
                "parsed": parsed,
                "first_try_valid": False,
                "final_valid": True,
                "num_retries": attempt - 1,
                "errors_seen": errors_seen,
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "estimated_cost": estimate_cost(total_input_tokens, total_output_tokens),
            }
        except (json.JSONDecodeError, ValidationError, Exception) as e:
            error_msg = str(e)
            errors_seen.append(f"Attempt {attempt}: {error_msg}")

        if attempt - 1 >= max_retries:
            break

    # All attempts failed
    return {
        "parsed": None,
        "first_try_valid": False,
        "final_valid": False,
        "num_retries": max_retries,
        "errors_seen": errors_seen,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "estimated_cost": estimate_cost(total_input_tokens, total_output_tokens),
    }
