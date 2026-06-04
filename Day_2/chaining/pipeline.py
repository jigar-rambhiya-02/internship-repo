import json
import os
import sys
import time
from pathlib import Path

from groq import Groq


MODEL = "openai/gpt-oss-120b"
BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
RUNS_DIR = BASE_DIR / "runs"
BRAND_RULES_PATH = BASE_DIR / "brand_rules.md"


api_key = os.getenv("GROQ_API_KEY")

# If you cannot use an environment variable, paste your key here instead:
# api_key = "YOUR_GROQ_API_KEY"

if not api_key:
    print("ERROR: GROQ_API_KEY is not set.")
    print('Set it with: export GROQ_API_KEY="YOUR_GROQ_API_KEY"')
    print("Or paste your key directly into pipeline.py where marked.")
    sys.exit(1)


client = Groq(api_key=api_key)


def read_text(path):
    if not path.exists():
        print(f"ERROR: Missing file: {path}")
        sys.exit(1)
    return path.read_text(encoding="utf-8").strip()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_json_strict(raw_text, step_name):
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as error:
        print(f"ERROR: {step_name} returned invalid JSON.")
        print(f"JSON error: {error}")
        print("Raw response:")
        print(raw_text)
        sys.exit(1)


def call_groq(system_prompt, user_prompt, temperature):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
    except Exception as error:
        print("ERROR: Groq API call failed.")
        print(f"Details: {error}")
        sys.exit(1)

    content = response.choices[0].message.content
    if content is None:
        print("ERROR: Groq API returned an empty message.")
        sys.exit(1)

    return content.strip()


def require_string(data, key, step_name):
    if key not in data:
        print(f"ERROR: {step_name} missing key: {key}. Received: {data}")
        sys.exit(1)
    if not isinstance(data[key], str) or not data[key].strip():
        print(f"ERROR: {step_name} key '{key}' must be a non-empty string. Received: {data}")
        sys.exit(1)


def validate_attributes(data):
    step_name = "Step 1"

    if not isinstance(data, dict):
        print(f"ERROR: {step_name} output must be a JSON object. Received: {data}")
        sys.exit(1)

    require_string(data, "product_name", step_name)
    require_string(data, "category", step_name)
    require_string(data, "target_audience", step_name)

    if "key_features" not in data:
        print(f"ERROR: {step_name} missing key: key_features. Received: {data}")
        sys.exit(1)

    if not isinstance(data["key_features"], list):
        print(f"ERROR: {step_name} key_features must be an array. Received: {data}")
        sys.exit(1)

    if not 3 <= len(data["key_features"]) <= 6:
        print(f"ERROR: {step_name} key_features must contain 3 to 6 items. Received: {data}")
        sys.exit(1)

    for index, feature in enumerate(data["key_features"], start=1):
        if not isinstance(feature, str) or not feature.strip():
            print(f"ERROR: {step_name} key_features item {index} must be a non-empty string. Received: {data}")
            sys.exit(1)


def validate_variants(data):
    step_name = "Step 2"

    if not isinstance(data, list):
        print(f"ERROR: {step_name} output must be a JSON array. Received: {data}")
        sys.exit(1)

    if len(data) != 3:
        print(f"ERROR: {step_name} must return exactly 3 variants. Received: {data}")
        sys.exit(1)

    for index, variant in enumerate(data, start=1):
        if not isinstance(variant, dict):
            print(f"ERROR: {step_name} variant {index} must be an object. Received: {data}")
            sys.exit(1)
        require_string(variant, "headline", f"{step_name} variant {index}")
        require_string(variant, "body", f"{step_name} variant {index}")


def validate_winner(data, variants):
    step_name = "Step 3"

    if not isinstance(data, dict):
        print(f"ERROR: {step_name} output must be a JSON object. Received: {data}")
        sys.exit(1)

    if "winner_index" not in data:
        print(f"ERROR: {step_name} missing key: winner_index. Received: {data}")
        sys.exit(1)

    if data["winner_index"] not in [1, 2, 3]:
        print(f"ERROR: {step_name} winner_index must be 1, 2, or 3. Received: {data}")
        sys.exit(1)

    if "winner" not in data:
        print(f"ERROR: {step_name} missing key: winner. Received: {data}")
        sys.exit(1)

    if not isinstance(data["winner"], dict):
        print(f"ERROR: {step_name} winner must be an object. Received: {data}")
        sys.exit(1)

    require_string(data["winner"], "headline", step_name)
    require_string(data["winner"], "body", step_name)
    require_string(data, "reason", step_name)

    selected_variant = variants[data["winner_index"] - 1]
    if data["winner"] != selected_variant:
        print(f"ERROR: {step_name} winner must exactly match variant {data['winner_index']}.")
        print(f"Expected: {selected_variant}")
        print(f"Received: {data['winner']}")
        sys.exit(1)


def step1_extract(brief_text):
    system_prompt = read_text(PROMPTS_DIR / "extract.txt")
    user_prompt = f"Product brief:\n{brief_text}"

    raw_response = call_groq(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.3,
    )

    attributes = load_json_strict(raw_response, "Step 1")
    validate_attributes(attributes)
    return attributes


def step2_generate(attributes_json):
    system_prompt = read_text(PROMPTS_DIR / "generate.txt")
    user_prompt = "Product attributes JSON:\n" + json.dumps(attributes_json, indent=2)

    raw_response = call_groq(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.7,
    )

    variants = load_json_strict(raw_response, "Step 2")
    validate_variants(variants)
    return variants


def step3_select(variants_list, brand_rules_text):
    system_prompt = read_text(PROMPTS_DIR / "select.txt")
    user_prompt = (
        "Ad variants JSON:\n"
        + json.dumps(variants_list, indent=2)
        + "\n\nBrand rules:\n"
        + brand_rules_text
    )

    raw_response = call_groq(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.3,
    )

    winner = load_json_strict(raw_response, "Step 3")
    validate_winner(winner, variants_list)
    return winner


def run_one_folder(run_folder, brand_rules_text):
    print(f"\n=== Running {run_folder.name} ===")

    brief_path = run_folder / "input_brief.txt"
    attributes_path = run_folder / "step1_attributes.json"
    variants_path = run_folder / "step2_variants.json"
    winner_path = run_folder / "step3_winner.json"

    brief_text = read_text(brief_path)

    print("Step 1: extracting attributes...")
    attributes = step1_extract(brief_text)
    write_json(attributes_path, attributes)
    print(f"Saved {attributes_path}")

    time.sleep(0.5)

    print("Step 2: generating ad variants...")
    variants = step2_generate(attributes)
    write_json(variants_path, variants)
    print(f"Saved {variants_path}")

    time.sleep(0.5)

    print("Step 3: selecting best variant...")
    winner = step3_select(variants, brand_rules_text)
    write_json(winner_path, winner)
    print(f"Saved {winner_path}")


def main():
    brand_rules_text = read_text(BRAND_RULES_PATH)

    for run_number in range(1, 6):
        run_folder = RUNS_DIR / f"run_{run_number}"
        if not run_folder.exists():
            print(f"ERROR: Missing run folder: {run_folder}")
            sys.exit(1)
        run_one_folder(run_folder, brand_rules_text)

    print("\nDone. All 5 runs completed successfully.")


if __name__ == "__main__":
    main()
