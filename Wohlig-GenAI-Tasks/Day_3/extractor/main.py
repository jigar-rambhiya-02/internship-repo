# main.py
"""
Usage:
    python main.py samples/invoice_001.txt

Reads a plain-text invoice, sends it to Gemini with a strict response_schema,
validates the returned JSON with Pydantic, prints it, and saves it to outputs/.
"""

import json
import os
import sys
from pathlib import Path

import google.generativeai as genai
from pydantic import ValidationError

from schema import Invoice


# ── Configuration ─────────────────────────────────────────────────────────────

GEMINI_MODEL = "gemini-1.5-flash"
OUTPUT_DIR = Path("outputs")


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        print(
            "\n[ERROR] GEMINI_API_KEY environment variable is not set.\n"
            "Fix: export GEMINI_API_KEY='your-key-here'\n"
            "Get a key at: https://aistudio.google.com/app/apikey\n"
        )
        sys.exit(1)
    return key


# ── Schema conversion ──────────────────────────────────────────────────────────

def pydantic_to_gemini_schema(model) -> dict:
    """
    Convert a Pydantic model's JSON schema into the format Gemini expects
    for response_schema. Gemini uses a restricted subset of JSON Schema.
    """
    raw = model.model_json_schema()
    return _clean_schema(raw, raw.get("$defs", {}))


def _clean_schema(schema: dict, defs: dict) -> dict:
    """
    Recursively resolve $ref references and strip keys Gemini doesn't accept.
    """
    # Resolve $ref
    if "$ref" in schema:
        ref_name = schema["$ref"].split("/")[-1]
        resolved = defs.get(ref_name, {})
        return _clean_schema(resolved, defs)

    result = {}

    if "type" in schema:
        result["type"] = schema["type"].upper()  # Gemini wants uppercase strings

    if "properties" in schema:
        result["type"] = "OBJECT"
        result["properties"] = {
            k: _clean_schema(v, defs)
            for k, v in schema["properties"].items()
        }
        # Mark required fields
        if "required" in schema:
            result["required"] = schema["required"]

    if "items" in schema:
        result["type"] = "ARRAY"
        result["items"] = _clean_schema(schema["items"], defs)

    if "enum" in schema:
        result["type"] = "STRING"
        result["enum"] = schema["enum"]

    # anyOf with null means Optional — use the non-null type
    if "anyOf" in schema:
        non_null = [s for s in schema["anyOf"] if s.get("type") != "null"]
        if non_null:
            return _clean_schema(non_null[0], defs)
        result["type"] = "STRING"  # fallback

    if schema.get("type") in ("number", "float"):
        result["type"] = "NUMBER"

    if schema.get("type") == "integer":
        result["type"] = "INTEGER"

    if schema.get("type") == "string":
        result["type"] = "STRING"

    if schema.get("type") == "boolean":
        result["type"] = "BOOLEAN"

    if schema.get("type") == "array":
        result["type"] = "ARRAY"

    return result


# ── Extraction ─────────────────────────────────────────────────────────────────

EXTRACTION_PROMPT = """\
You are a document extraction assistant. Extract all invoice fields from the
document below and return them as structured JSON matching the schema exactly.

Rules:
- invoice_date and due_date must be ISO format YYYY-MM-DD if present.
- currency must be a three-letter ISO code (e.g. USD, EUR, GBP, INR).
- status must be one of: paid, unpaid, overdue, partially_paid, unknown.
- subtotal, tax_amount, and total_amount must be numeric (float).
- line_item totals must equal quantity × unit_price (do not round arbitrarily).
- If a field is not present in the document and is optional, omit it or use null.
- Do not invent data. If you cannot determine a value, use null for optional fields
  or your best reasonable extraction for required fields.

DOCUMENT:
{document_text}
"""


def extract_invoice(file_path: Path) -> Invoice:
    if not file_path.exists():
        print(f"\n[ERROR] File not found: {file_path}\n")
        sys.exit(1)

    document_text = file_path.read_text(encoding="utf-8")
    if not document_text.strip():
        print(f"\n[ERROR] File is empty: {file_path}\n")
        sys.exit(1)

    api_key = get_api_key()
    genai.configure(api_key=api_key)

    # Build Gemini response schema from Pydantic model
    response_schema = pydantic_to_gemini_schema(Invoice)

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
        ),
    )

    prompt = EXTRACTION_PROMPT.format(document_text=document_text)

    try:
        response = model.generate_content(prompt)
    except Exception as e:
        print(f"\n[ERROR] Gemini API call failed: {e}\n")
        sys.exit(1)

    raw_text = response.text
    if not raw_text or not raw_text.strip():
        print("\n[ERROR] Gemini returned an empty response.\n")
        sys.exit(1)

    # Parse JSON
    try:
        raw_data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"\n[ERROR] Gemini returned malformed JSON.\nError: {e}\nRaw response:\n{raw_text}\n")
        sys.exit(1)

    # Validate with Pydantic
    try:
        invoice = Invoice.model_validate(raw_data)
    except ValidationError as e:
        print(f"\n[ERROR] Pydantic validation failed.\nValidation errors:\n{e}\n")
        print(f"Raw data received:\n{json.dumps(raw_data, indent=2)}")
        sys.exit(1)

    return invoice


# ── Save output ────────────────────────────────────────────────────────────────

def save_output(invoice: Invoice, input_path: Path) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    stem = input_path.stem  # e.g. "invoice_001"
    out_path = OUTPUT_DIR / f"{stem}.extracted.json"
    out_path.write_text(
        invoice.model_dump_json(indent=2, exclude_none=False),
        encoding="utf-8",
    )
    return out_path


# ── Entrypoint ─────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py samples/invoice_001.txt")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    print(f"\nExtracting: {input_path}")

    invoice = extract_invoice(input_path)
    out_path = save_output(invoice, input_path)

    print(f"\n── Extracted Invoice ──────────────────────────────")
    print(invoice.model_dump_json(indent=2))
    print(f"\n── Saved to: {out_path}\n")


if __name__ == "__main__":
    main()