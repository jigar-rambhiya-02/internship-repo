from __future__ import annotations

import csv
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import time

# Load environment variables from .env file if present
load_dotenv()

# Allowed categories
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
MODEL_NAME = "llama-3.3-70b-versatile"


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIR / name
    return prompt_path.read_text(encoding="utf-8")


def clean_prediction(text: str) -> str:
    """Normalize model output to one of the allowed category labels."""
    prediction = text.strip().strip('"').strip("'")

    if prediction in CATEGORIES:
        return prediction

    lowered = prediction.lower()
    for category in CATEGORIES:
        if category.lower() in lowered:
            return category

    return "Other"


def ask_llm(client: Groq, prompt_template: str, ticket_text: str) -> str:
    """
    Send a prompt to the Groq API and return a cleaned category prediction.
    """
    # Replace the placeholder with the actual ticket text
    prompt = prompt_template.replace("{{ticket_text}}", ticket_text)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=20,
        )
        raw_output = response.choices[0].message.content
        return clean_prediction(raw_output or "")
    
    except Exception as e:
        print(f"Error during API calling: {e}")
        return "Other"


def main() -> None:
    # Check for API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Set GROQ_API_KEY environment variable before running this script.\n ")

    # Initialize Groq client
    client = Groq(api_key=api_key)

    # Load prompt templates
    prompt_templates = {
        "zero_shot_pred": load_prompt("zero_shot.txt"),
        "few_shot_pred": load_prompt("few_shot.txt"),
        "role_based_pred": load_prompt("role_based.txt"),
    }

    # Read input CSV
    with INPUT_CSV.open(newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        original_fieldnames = reader.fieldnames or []
        rows = list(reader)

    # Prepare output fieldnames (original columns + prediction columns)
    output_fieldnames = original_fieldnames + list(prompt_templates.keys())

    # Process each row and add predictions
    for row in rows:
        ticket_text = row.get("ticket_text", "")
        if not ticket_text:
            # If ticket_text is missing, fill predictions with "Other"
            for col in prompt_templates:
                row[col] = "Other"
            continue

        for col, template in prompt_templates.items():
            prediction = ask_llm(client, template, ticket_text)
            row[col] = prediction
            # Small delay to avoid hitting rate limits (adjust as needed)
            time.sleep(2)   # optional

    # Write output CSV
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Predictions written to {OUTPUT_CSV}")
    print("The Output CSV is Done!")


if __name__ == "__main__":
    main()