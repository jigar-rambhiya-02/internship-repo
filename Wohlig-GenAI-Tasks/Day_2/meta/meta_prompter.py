#!/usr/bin/env python3
"""
meta_prompter.py

Usage:
    python meta_prompter.py "your vague brief here"

Takes a vague user brief, loads the meta-prompt, calls the Groq API,
prints the structured prompt to stdout, and saves it to generated_prompts/.
"""

import os
import sys
import re
from pathlib import Path

# Load .env before anything else — this lets GROQ_API_KEY live in a .env file
# rather than being set in the shell. If the key is already in the environment,
# load_dotenv() will not overwrite it.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional — if missing, rely on environment variables only
    pass

from groq import Groq, APIStatusError, APIConnectionError, APITimeoutError


# ── Constants ──────────────────────────────────────────────────────────────────

MODEL = "openai/gpt-oss-120b"
MAX_TOKENS = 2048  # structured prompts can be long; give the model room
TEMPERATURE = 0.4  # low-ish to keep output consistent, not too low to avoid repetition

# Resolve all paths relative to this script's location.
# This means you can call the script from any working directory and it will
# still find meta_prompt.txt and the generated_prompts/ folder correctly.
SCRIPT_DIR = Path(__file__).parent.resolve()
META_PROMPT_PATH = SCRIPT_DIR / "meta_prompt.txt"
OUTPUT_DIR = SCRIPT_DIR / "generated_prompts"


# ── Helpers ────────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """
    Convert a vague brief string into a safe filename.
    Example: "extract data from PDFs" → "extract_data_from_pdfs"
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)   # remove punctuation
    text = re.sub(r"[\s-]+", "_", text)    # replace spaces/hyphens with underscores
    text = re.sub(r"_+", "_", text)        # collapse multiple underscores
    return text[:80]                        # truncate to avoid filesystem limits


def load_meta_prompt() -> str:
    """
    Load meta_prompt.txt. Exits with a clear message if the file is missing.
    """
    if not META_PROMPT_PATH.exists():
        print(
            f"ERROR: meta_prompt.txt not found.\n"
            f"Expected it at: {META_PROMPT_PATH}\n"
            f"Create it by following Section 3 of guide.md.",
            file=sys.stderr,
        )
        sys.exit(1)

    content = META_PROMPT_PATH.read_text(encoding="utf-8").strip()

    if not content:
        print(
            f"ERROR: meta_prompt.txt is empty.\n"
            f"File path: {META_PROMPT_PATH}\n"
            f"Copy the content from Section 3 of guide.md into it.",
            file=sys.stderr,
        )
        sys.exit(1)

    return content


def get_api_key() -> str:
    """
    Retrieve the Groq API key from the environment. Exits if not set.
    """
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        print(
            "ERROR: GROQ_API_KEY is not set.\n"
            "Set it with:\n"
            "  export GROQ_API_KEY='gsk_your_key_here'   # Linux/Mac\n"
            "  set GROQ_API_KEY=gsk_your_key_here        # Windows CMD\n"
            "Or add it to a .env file in the meta/ directory.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def save_output(slug: str, content: str) -> Path:
    """
    Save the generated prompt to generated_prompts/<slug>.txt.
    Creates the output directory if it doesn't exist.
    Returns the path where the file was saved.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{slug}.txt"

    try:
        output_path.write_text(content, encoding="utf-8")
    except PermissionError:
        print(
            f"ERROR: Cannot write to {output_path}\n"
            f"Check that you have write permissions to: {OUTPUT_DIR}",
            file=sys.stderr,
        )
        # Don't exit — the output was printed to stdout, so it's not lost
        return output_path

    return output_path


def call_groq(client: Groq, system_prompt: str, user_brief: str) -> str:
    """
    Call the Groq API and return the generated text.
    Raises descriptive errors for each failure mode instead of swallowing them.
    """
    # The meta-prompt is the system message. The user brief is the user message.
    # This separation keeps the meta-prompt reusable across briefs without
    # re-sending it as part of user content (cleaner token accounting too).
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_brief},
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
    except APIStatusError as e:
        # Covers 429 rate limit, 401 auth errors, 500 server errors, etc.
        print(
            f"ERROR: Groq API returned status {e.status_code}.\n"
            f"Message: {e.message}\n"
            f"Type: {type(e).__name__}",
            file=sys.stderr,
        )
        raise  # re-raise so the caller can decide whether to retry or exit
    except APIConnectionError as e:
        print(
            f"ERROR: Could not connect to the Groq API.\n"
            f"Check your internet connection.\n"
            f"Details: {e}",
            file=sys.stderr,
        )
        raise
    except APITimeoutError as e:
        print(
            f"ERROR: Groq API request timed out.\n"
            f"The model may be overloaded. Try again in a few seconds.\n"
            f"Details: {e}",
            file=sys.stderr,
        )
        raise

    # Extract the text content from the response
    if not response.choices:
        print("WARNING: Groq returned an empty choices list.", file=sys.stderr)
        return ""

    message = response.choices[0].message
    content = message.content

    if content is None:
        print(
            "WARNING: Groq returned a message with null content.\n"
            "This can happen if the model triggered a content filter.",
            file=sys.stderr,
        )
        return ""

    return content.strip()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    # 1. Validate CLI input
    if len(sys.argv) < 2:
        print(
            "Usage: python meta_prompter.py \"your vague brief here\"\n"
            'Example: python meta_prompter.py "extract data from PDFs"',
            file=sys.stderr,
        )
        sys.exit(1)

    # Join all positional args in case the user forgot to quote the brief.
    # "extract data from PDFs" passed without quotes becomes multiple argv items.
    user_brief = " ".join(sys.argv[1:]).strip()

    if not user_brief:
        print("ERROR: Brief cannot be empty.", file=sys.stderr)
        sys.exit(1)

    slug = slugify(user_brief)
    print(f"Brief   : {user_brief}")
    print(f"Slug    : {slug}")
    print(f"Model   : {MODEL}")
    print("-" * 60)

    # 2. Load prerequisites
    api_key = get_api_key()
    meta_prompt = load_meta_prompt()

    # 3. Build the Groq client
    client = Groq(api_key=api_key)

    # 4. Call the API
    print("Calling Groq API...")
    try:
        generated = call_groq(client, meta_prompt, user_brief)
    except (APIStatusError, APIConnectionError, APITimeoutError):
        # Error already printed in call_groq; exit cleanly
        sys.exit(1)

    # 5. Handle empty/malformed response
    if not generated:
        print(
            "WARNING: The API returned an empty or null response.\n"
            "Saving an empty file anyway. Check the Groq dashboard for details.",
            file=sys.stderr,
        )
        generated = "[EMPTY RESPONSE — check API logs]"

    # 6. Print to stdout
    print("\n" + "=" * 60)
    print(generated)
    print("=" * 60 + "\n")

    # 7. Save to file
    output_path = save_output(slug, generated)
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()