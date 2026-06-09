# evaluate.py
"""
Evaluates extraction accuracy by comparing extracted JSON files against ground truth.

Usage:
    python evaluate.py

Reads:
    ground_truth.jsonl
    outputs/invoice_XXX.extracted.json (one per sample)

Writes:
    field_accuracy.csv
    (prints accuracy summary to stdout)
"""

import csv
import json
from pathlib import Path


GROUND_TRUTH_FILE = Path("ground_truth.jsonl")
OUTPUTS_DIR = Path("outputs")
CSV_OUTPUT = Path("field_accuracy.csv")


# ── Flattening ─────────────────────────────────────────────────────────────────

def flatten(obj, prefix=""):
    """
    Recursively flatten a nested dict/list into dot-notation keys.

    Examples:
        {"vendor": {"name": "Acme"}}  →  {"vendor.name": "Acme"}
        {"line_items": [{"description": "X"}]}  →  {"line_items": <json>}

    Lists are stored as their full JSON string for comparison.
    """
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)):
                items.update(flatten(v, full_key))
            else:
                items[full_key] = v
    elif isinstance(obj, list):
        # Store list fields as canonical JSON strings for exact comparison
        items[prefix] = json.dumps(obj, sort_keys=True)
    else:
        items[prefix] = obj
    return items


# ── Comparison ─────────────────────────────────────────────────────────────────

def compare(extracted: dict, ground_truth: dict) -> list[dict]:
    """
    Compare extracted and ground truth field by field.
    Returns a list of result rows for the CSV.
    """
    flat_extracted = flatten(extracted)
    flat_truth = flatten(ground_truth)

    all_keys = set(flat_extracted.keys()) | set(flat_truth.keys())
    rows = []

    for field in sorted(all_keys):
        ext_val = flat_extracted.get(field, None)
        gt_val = flat_truth.get(field, None)

        # Normalize for comparison: strip whitespace, lowercase strings
        def norm(v):
            if v is None:
                return None
            if isinstance(v, str):
                return v.strip().lower()
            if isinstance(v, float):
                return round(v, 2)
            return v

        exact_match = norm(ext_val) == norm(gt_val)
        rows.append({
            "field_name": field,
            "extracted_value": ext_val,
            "ground_truth_value": gt_val,
            "exact_match": exact_match,
        })

    return rows


# ── Main ───────────────────────────────────────────────────────────────────────

def load_ground_truth() -> list[dict]:
    if not GROUND_TRUTH_FILE.exists():
        print(f"[ERROR] {GROUND_TRUTH_FILE} not found.")
        return []
    records = []
    with GROUND_TRUTH_FILE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def main():
    ground_truths = load_ground_truth()
    if not ground_truths:
        print("No ground truth records found. Exiting.")
        return

    all_rows = []
    missing_files = []

    for gt_record in ground_truths:
        sample_id = gt_record["sample_id"]
        file_name = gt_record["file_name"]  # e.g. "invoice_001.txt"
        stem = Path(file_name).stem         # "invoice_001"
        extracted_path = OUTPUTS_DIR / f"{stem}.extracted.json"

        if not extracted_path.exists():
            missing_files.append(str(extracted_path))
            continue

        with extracted_path.open(encoding="utf-8") as f:
            extracted = json.load(f)

        expected = gt_record["expected"]
        rows = compare(extracted, expected)

        for row in rows:
            row["sample_id"] = sample_id
            all_rows.append(row)

    if missing_files:
        print(f"\n[WARNING] Missing extracted files (run main.py first):")
        for mf in missing_files:
            print(f"  {mf}")

    if not all_rows:
        print("No comparison data. Nothing to write.")
        return

    # Write CSV
    fieldnames = ["sample_id", "field_name", "extracted_value", "ground_truth_value", "exact_match"]
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nWrote {len(all_rows)} rows to {CSV_OUTPUT}")

    # Print summary
    total = len(all_rows)
    correct = sum(1 for r in all_rows if r["exact_match"])
    overall = correct / total * 100 if total > 0 else 0
    print(f"\nOverall field accuracy: {correct}/{total} = {overall:.1f}%")

    # Per-field accuracy
    field_stats: dict[str, dict] = {}
    for row in all_rows:
        fn = row["field_name"]
        if fn not in field_stats:
            field_stats[fn] = {"correct": 0, "total": 0}
        field_stats[fn]["total"] += 1
        if row["exact_match"]:
            field_stats[fn]["correct"] += 1

    print("\nPer-field accuracy:")
    print(f"{'Field':<40} {'Correct':>8} {'Total':>7} {'Acc%':>8}")
    print("-" * 65)
    for fn, stats in sorted(field_stats.items()):
        acc = stats["correct"] / stats["total"] * 100
        print(f"{fn:<40} {stats['correct']:>8} {stats['total']:>7} {acc:>7.1f}%")


if __name__ == "__main__":
    main()