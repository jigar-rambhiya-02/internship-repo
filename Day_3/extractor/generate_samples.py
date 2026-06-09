# generate_samples.py
"""
Uses Gemini to generate 10 synthetic B2B invoice text files and saves them
into samples/. Run this once if you want Gemini-generated variation
instead of the hand-written samples in the guide.

Usage:
    python generate_samples.py
"""

import os
import sys
from pathlib import Path
import google.generativeai as genai


SAMPLES_DIR = Path("samples")
GEMINI_MODEL = "gemini-1.5-flash"

GENERATION_PROMPT = """\
Generate a realistic plain-text B2B invoice as it would appear in a scanned or
digital document. The invoice should be for {description}.

Requirements:
- Invoice number in format INV-XXXX
- Invoice date and due date in a natural format (e.g. "15 March 2024")
- Vendor name, address, tax ID, email
- Buyer name, address
- {extra_requirements}
- Line items with description, quantity, unit price, and line total
- Subtotal, tax amount (label it clearly), and total amount
- Currency: {currency}
- Status note at the bottom: {status}
- Realistic company names, addresses, and product/service names

Return only the plain text of the invoice. No JSON. No markdown. No explanation.
"""

SAMPLE_SPECS = [
    {"id": "001", "description": "software consulting services", "currency": "USD", "status": "UNPAID",
     "extra": "Include a purchase order number PO-2024-0091"},
    {"id": "002", "description": "office furniture and supplies", "currency": "EUR", "status": "PAID",
     "extra": "Add a note that payment was received"},
    {"id": "003", "description": "cloud hosting services with multiple line items (at least 6)", "currency": "GBP", "status": "OVERDUE",
     "extra": "No purchase order number"},
    {"id": "004", "description": "marketing and design services", "currency": "INR", "status": "PARTIALLY PAID",
     "extra": "Include a note about the remaining balance due"},
    {"id": "005", "description": "laboratory equipment", "currency": "USD", "status": "UNPAID",
     "extra": "Omit the due date entirely"},
    {"id": "006", "description": "logistics and freight services", "currency": "AED", "status": "PAID",
     "extra": "Include a purchase order number"},
    {"id": "007", "description": "IT hardware procurement", "currency": "SGD", "status": "UNPAID",
     "extra": "Use unusual spacing and alignment (simulate a poorly formatted scan)"},
    {"id": "008", "description": "legal consulting services", "currency": "USD", "status": "OVERDUE",
     "extra": "No purchase order number. Add a late payment notice"},
    {"id": "009", "description": "advertising agency retainer", "currency": "CAD", "status": "UNPAID",
     "extra": "Include purchase order number PO-CA-7721"},
    {"id": "010", "description": "construction materials", "currency": "ZAR", "status": "PARTIALLY PAID",
     "extra": "Include 8 line items and a note about delivery charges"},
]


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        print("[ERROR] GEMINI_API_KEY not set.")
        sys.exit(1)
    return key


def main():
    SAMPLES_DIR.mkdir(exist_ok=True)
    genai.configure(api_key=get_api_key())
    model = genai.GenerativeModel(GEMINI_MODEL)

    for spec in SAMPLE_SPECS:
        out_path = SAMPLES_DIR / f"invoice_{spec['id']}.txt"
        if out_path.exists():
            print(f"[SKIP] {out_path} already exists.")
            continue

        prompt = GENERATION_PROMPT.format(
            description=spec["description"],
            currency=spec["currency"],
            status=spec["status"],
            extra_requirements=spec["extra"],
        )
        print(f"Generating invoice_{spec['id']}.txt ...")
        try:
            response = model.generate_content(prompt)
            out_path.write_text(response.text.strip(), encoding="utf-8")
            print(f"  Saved → {out_path}")
        except Exception as e:
            print(f"  [ERROR] {e}")


if __name__ == "__main__":
    main()