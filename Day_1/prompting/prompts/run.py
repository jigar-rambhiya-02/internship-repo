"""
Run zero-shot, few-shot, and role-based prompts on support tickets with Gemini Flash.

Setup:
  pip install google-genai
  export GEMINI_API_KEY="your_api_key_here"

Run:
  python prompting/predict_styles.py

The script reads:
  prompting/styles_eval.csv
  prompting/prompts/zero_shot.txt
  prompting/prompts/few_shot.txt
  prompting/prompts/role_based.txt

It writes:
  prompting/styles_eval_predictions.csv
"""

from __future__ import annotations

import csv
import os
import time
from pathlib import Path

import groq


CATEGORIES = {
    "Refund",
    "Shipping",
    "Login",
    "Payment",
    "Account",
    "Product Quality",
    "Order Change",
    "Other",
}

BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "styles_eval.csv"
OUTPUT_CSV = BASE_DIR / "styles_eval_predictions.csv"
PROMPTS_DIR = BASE_DIR / "prompts"
MODEL_NAME = "llama-3.1-8b-instant"

def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def clean_prediction(text: str) -> str:
    """Normalize Gemini output to one of the allowed category labels."""
    prediction = text.strip().strip('"').strip("'")

    if prediction in CATEGORIES:
        return prediction

    lowered = prediction.lower()
    for category in CATEGORIES:
        if category.lower() in lowered:
            return category

    return "Other"


def ask_gemini(client: grop.Client, prompt_template: str, ticket_text: str) -> str:
    prompt = prompt_template.replace("{{ticket_text}}", ticket_text)
    response = client.chat.completions.create(  
        model=MODEL_NAME,
        contents=prompt,
        config={
            "temperature": 0,
            "max_output_tokens": 20,
        },
    )
    return clean_prediction(response.text or "")


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def main() -> None:
    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError("Set GEMINI_API_KEY before running this script.")

    # client = groq.Groq(api_key='***REMOVED***')
    client = groq.Groq(api_key=os.environ["***REMOVED***"])
    prompt_templates = {
        "zero_shot_pred": load_prompt("zero_shot.txt"),
        "few_shot_pred": load_prompt("few_shot.txt"),
        "role_based_pred": load_prompt("role_based.txt"),
    }

    with INPUT_CSV.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    for row in rows:
        ticket_text = row["ticket_text"]