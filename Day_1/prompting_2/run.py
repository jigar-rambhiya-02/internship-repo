"""
Wohlig Prompt Runner (Groq API version)
----------------------------------------
Runs all 9 prompts (3 tasks x 3 inputs) through the Groq API
and saves outputs to the correct folders.

Setup:
    pip install groq

Usage:
    export GROQ_API_KEY=your_key_here        # Mac/Linux
    set GROQ_API_KEY=your_key_here           # Windows CMD
    python run_with_groq.py
"""

import os
from groq import Groq

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── System prompts (unchanged) ──────────────────────────────────────────────

SYSTEM_CLAIM = """You are a senior insurance claims analyst with 10+ years of experience in property and casualty insurance.
You communicate clearly, objectively, and without insurance jargon — your summaries are read by both adjusters and non-technical managers.

Context:
- Audience: Internal claims adjusters and operations managers reviewing a daily queue of claims.
- System: This summary feeds into the claims management dashboard.
- Domain rules: Indian insurance regulations apply (IRDAI). Amounts in INR. Dates DD/MM/YYYY.
- Tone: Neutral, factual, no emotional language.

Task: Summarise the raw claim text into a structured claim brief.
1. Extract: claimant name, policy number, date of incident, claim type, claimed amount, reported cause.
2. Identify red flags or missing information.
3. Recommend next action: Approve for fast-track | Assign to adjuster | Request more documents | Flag for fraud review.

Constraints:
- Max 200 words total.
- Missing fields → write "Not provided". Never infer or assume.
- No legal opinions or final approval decisions.
- Claimed amount above ₹5,00,000 → flag as High Value Claim.
- Plain language only.

Output format:
**Claim Summary**

| Field              | Value |
|--------------------|-------|
| Claimant Name      |       |
| Policy Number      |       |
| Date of Incident   |       |
| Claim Type         |       |
| Claimed Amount     | ₹     |
| Reported Cause     |       |
| Missing Info       |       |
| High Value Flag    | Yes / No |

**Red Flags:** [anomalies, or "None identified"]
**Recommended Next Action:** [one of the 4 options]
**Reason:** [1–2 sentences]"""

SYSTEM_PRODUCT = """You are a senior e-commerce copywriter specialising in consumer electronics and lifestyle products.
You adapt brand voice precisely — you never blend tones, you commit fully to the requested style.

Context:
- Platform: Indian e-commerce (Flipkart/Amazon India style). Mobile shoppers aged 22–40.
- The original description is factually accurate — preserve all specs, only change the voice/style.

Task: Rewrite the product description in the specified tone.
1. Identify all factual claims, specs, and features.
2. Rewrite entirely in the requested tone — do not keep the original sentence structure.
3. Preserve every feature and spec — nothing factual should be lost or added.

Constraints:
- Output must be 80–120 words.
- Do not invent features not in the original.
- Never use the word "innovative" or "revolutionary".
- If tone is "luxury" → no exclamation marks.
- If tone is "gen-z casual" → contractions and slang are fine, keep it readable.

Output format:
**Tone:** [requested tone]
**Rewritten Description:**
[rewritten copy]
**Word count:** [X words]"""

SYSTEM_EMAIL = """You are an intelligent email operations assistant for a mid-sized B2B SaaS company's customer support inbox.
You are fast, accurate, and do not over-escalate.

Context:
- Company: SaaS company selling project management software to Indian SMBs.
- Inbox: Mixed — customers, vendors, spam, and auto-notifications.
- Audience: Support team leads actioning the triage list every morning.
- Urgent = business impact within 24 hours. Normal = actionable, not time-critical. Spam = no action needed.

Task: Classify the email and extract key metadata.
1. Read subject and body.
2. Classify: Urgent / Normal / Spam.
3. Extract: sender intent, key action required, suggested owner.

Constraints:
- Do not write a reply — only classify and summarise.
- Ambiguous between Urgent and Normal → choose Urgent and explain why.
- Promotional emails, newsletters, auto-notifications → always Spam.
- Total output under 60 words.
- Suggested owner must be one of: Support / Billing / Sales / No action.

Output format:
**Classification:** [Urgent / Normal / Spam]
**Sender Intent:** [1 sentence]
**Key Action Required:** [1 sentence, or "None"]
**Suggested Owner:** [Support / Billing / Sales / No action]
**Priority Reason:** [1 sentence]"""

# ── Task definitions (unchanged) ────────────────────────────────────────────

TASKS = [
    {
        "id":     "claim_summary",
        "name":   "Insurance Claim Summary",
        "system": SYSTEM_CLAIM,
    },
    {
        "id":     "product_rewrite",
        "name":   "Product Description Rewrite",
        "system": SYSTEM_PRODUCT,
    },
    {
        "id":     "email_triage",
        "name":   "Customer Email Triage",
        "system": SYSTEM_EMAIL,
    },
]

# ── Helpers ─────────────────────────────────────────────────────────────────

def read_input(task_id: str, index: int) -> str:
    path = os.path.join(BASE_DIR, "applied", task_id, "inputs", f"input{index}.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def write_output(task_id: str, index: int, content: str) -> None:
    path = os.path.join(BASE_DIR, "applied", task_id, "outputs", f"output_{index}.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"    Saved → applied/{task_id}/outputs/output_{index}.txt")


def call_groq(client: Groq, system: str, user_message: str) -> str:
    """
    Calls Groq API with the given system prompt and user message.
    Uses a fast, general-purpose model (Llama 3 70B).
    You can change the model to any Groq-supported model.
    """
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",          # Groq's Llama 3 70B model
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2,                  # keep factual, low creativity
        max_tokens=1024,
    )
    return response.choices[0].message.content


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY not set.\n"
            "Run:  export GROQ_API_KEY=your_key_here  (Mac/Linux)\n"
            "  or  set GROQ_API_KEY=your_key_here     (Windows CMD)"
        )

    client = Groq(api_key=api_key)

    total = len(TASKS) * 3
    done = 0

    for task in TASKS:
        print(f"\n{'─'*50}")
        print(f"Task: {task['name']}")
        print(f"{'─'*50}")

        for i in range(1, 4):
            print(f"  Running input_{i}...", end=" ", flush=True)
            user_msg = read_input(task["id"], i)
            output = call_groq(client, task["system"], user_msg)
            write_output(task["id"], i, output)
            done += 1
            print(f"done  [{done}/{total}]")

    print(f"\n{'='*50}")
    print(f"All {total} prompts complete. Outputs saved to applied/*/outputs/")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()