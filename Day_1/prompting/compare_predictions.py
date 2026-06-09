import csv

INPUT_CSV = "styles_eval_predictions.csv"
OUTPUT_CSV = "styles_eval_with_flags.csv"

# Prediction column names (as they appear in the file)
PRED_COLUMNS = ["zero_shot_pred", "few_shot_pred", "role_based_pred"]

# Read the original CSV
with open(INPUT_CSV, newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)
    original_fieldnames = reader.fieldnames

# Define new column names for the truth flags
new_columns = [col.replace("_pred", "_correct") for col in PRED_COLUMNS]

# Output fieldnames = original + new columns
output_fieldnames = original_fieldnames + new_columns

# Initialize counters for accuracy
total = len(rows)
correct_counts = {col: 0 for col in PRED_COLUMNS}

# Process each row: add True/False and count correct predictions
for row in rows:
    ground = row["ground_truth"]
    for pred_col, new_col in zip(PRED_COLUMNS, new_columns):
        is_correct = (row[pred_col] == ground)
        row[new_col] = is_correct
        if is_correct:
            correct_counts[pred_col] += 1

# Write the new CSV with flags
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
    writer.writeheader()
    writer.writerows(rows)

# Print accuracy results
print(f"Total tickets processed: {total}")
print("\nAccuracy per prompting method:")
for pred_col in PRED_COLUMNS:
    acc = (correct_counts[pred_col] / total) * 100
    print(f"  {pred_col}: {correct_counts[pred_col]}/{total} ({acc:.1f}%)")

# Optional: overall average accuracy across three methods
avg_acc = sum(correct_counts.values()) / (len(PRED_COLUMNS) * total) * 100
print(f"\nAverage accuracy across all methods: {avg_acc:.1f}%")

print(f"\nDetailed output saved to {OUTPUT_CSV}")