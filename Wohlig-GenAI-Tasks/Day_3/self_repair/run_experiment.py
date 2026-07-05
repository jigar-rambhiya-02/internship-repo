# run_experiment.py
# Loads all .txt files from inputs/, runs each through the repair loop,
# writes results.csv, and prints a summary.

import csv
import os
from pathlib import Path

from repair_loop import run_repair_loop

INPUTS_DIR = Path("inputs")
RESULTS_CSV = Path("results.csv")

CSV_FIELDS = [
    "input_id",
    "first_try_valid",
    "final_valid",
    "num_retries",
    "errors_seen",
    "total_cost",
]


def main():
    input_files = sorted(INPUTS_DIR.glob("*.txt"))
    if not input_files:
        print("No .txt files found in inputs/. Please create them first.")
        return

    results = []
    total_cost = 0.0

    for filepath in input_files:
        input_id = filepath.stem  # e.g. "input_01"
        raw_text = filepath.read_text(encoding="utf-8")

        print(f"Processing {input_id}...", end=" ", flush=True)

        result = run_repair_loop(raw_text, max_retries=3)

        status = "✓" if result["final_valid"] else "✗"
        retries = result["num_retries"]
        print(f"{status}  (retries: {retries}, cost: ${result['estimated_cost']:.6f})")

        total_cost += result["estimated_cost"]

        results.append({
            "input_id": input_id,
            "first_try_valid": result["first_try_valid"],
            "final_valid": result["final_valid"],
            "num_retries": result["num_retries"],
            "errors_seen": " | ".join(result["errors_seen"]),
            "total_cost": round(result["estimated_cost"], 6),
        })

    # Write CSV
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults written to {RESULTS_CSV}\n")

    # Summary
    n = len(results)
    first_try_ok = sum(1 for r in results if r["first_try_valid"])
    final_ok = sum(1 for r in results if r["final_valid"])
    failed = n - final_ok

    print("=" * 50)
    print("EXPERIMENT SUMMARY")
    print("=" * 50)
    print(f"Total inputs:                  {n}")
    print(f"Valid on first attempt:        {first_try_ok} / {n}  ({100*first_try_ok/n:.1f}%)")
    print(f"Valid after repair loop:       {final_ok} / {n}  ({100*final_ok/n:.1f}%)")
    print(f"Failed after all retries:      {failed}")
    print(f"Success rate WITHOUT repair:   {100*first_try_ok/n:.1f}%")
    print(f"Success rate WITH repair:      {100*final_ok/n:.1f}%")
    print(f"Total estimated cost:          ${total_cost:.4f} USD")
    print("=" * 50)


if __name__ == "__main__":
    main()
