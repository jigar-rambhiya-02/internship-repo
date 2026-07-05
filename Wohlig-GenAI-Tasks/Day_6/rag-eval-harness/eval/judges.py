# eval/judges.py
import json
import re

from groq import Groq
import os

from dotenv import load_dotenv
from config import settings
from src.utils import setup_logger

load_dotenv('/Users/jigar/Documents/jigar/Tasks/.env')

api_key = os.getenv("GROQ_API_KEY") 
logger = setup_logger(__name__)


def _parse_judge_response(response_text: str) -> dict:
    """
    Defensive JSON parser for LLM judge outputs.
    Strips markdown fences, preamble, and extracts the first JSON object.
    """
    text = response_text.strip()

    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from response: {response_text[:200]}")


def _call_judge(prompt: str, client: Groq) -> dict:
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert evaluator. Output ONLY valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=512,
        )
        raw = response.choices[0].message.content.strip()
        parsed = _parse_judge_response(raw)

        score = parsed.get("score")
        reasoning = parsed.get("reasoning", "No reasoning provided.")

        if score is None:
            raise ValueError("Missing 'score' key in judge response")

        try:
            score = float(score)
        except (ValueError, TypeError):
            raise ValueError(f"Score is not a float: {score}")

        if not (0.0 <= score <= 1.0):
            logger.warning(f"Score {score} out of bounds; clamping to [0.0, 1.0]")
            score = max(0.0, min(1.0, score))

        return {"score": score, "reasoning": str(reasoning)}

    except Exception as e:
        logger.error(f"Judge call failed: {e}", exc_info=True)
        return {"score": None, "reasoning": "JUDGE_ERROR"}


def judge_faithfulness(
    question: str,
    answer: str,
    retrieved_chunks: list[str],
    ground_truth_answer: str,
    ground_truth_chunk_ids: list[str],
    retrieved_chunk_ids: list[str],
    client: Groq,
) -> dict:
    context_text = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""You are an expert evaluator assessing the FAITHFULNESS of a generated answer.
Faithfulness measures whether the answer sticks strictly to the retrieved context with zero hallucination.

QUESTION: {question}

GENERATED ANSWER: {answer}

RETRIEVED CONTEXT:
{context_text}

Evaluate whether every claim, fact, and statement in the GENERATED ANSWER is directly supported by the RETRIEVED CONTEXT.
- 1.0 = Every claim is directly supported by the context. Zero hallucination.
- 0.7-0.9 = Minor unsupported inferences or slight embellishments, but core claims are supported.
- 0.4-0.6 = Some claims are unsupported, or the answer mixes supported facts with hallucinated details.
- 0.1-0.3 = Most claims are unsupported or the answer contradicts the context.
- 0.0 = The answer completely ignores or contradicts the context.

Output ONLY a JSON object in this exact format:
{{"score": <float between 0.0 and 1.0>, "reasoning": "<detailed explanation>"}}

Do not include any markdown formatting, preamble, or text outside the JSON object."""

    return _call_judge(prompt, client)


def judge_answer_relevance(
    question: str,
    answer: str,
    retrieved_chunks: list[str],
    ground_truth_answer: str,
    ground_truth_chunk_ids: list[str],
    retrieved_chunk_ids: list[str],
    client: Groq,
) -> dict:
    prompt = f"""You are an expert evaluator assessing ANSWER RELEVANCE.
Answer relevance measures whether the generated answer actually and completely addresses the question asked.

QUESTION: {question}

GENERATED ANSWER: {answer}

GROUND TRUTH ANSWER: {ground_truth_answer}

Evaluate how well the GENERATED ANSWER addresses the QUESTION.
- 1.0 = The answer fully and accurately addresses every aspect of the question.
- 0.7-0.9 = The answer addresses the question well but misses minor nuances.
- 0.4-0.6 = The answer partially addresses the question or misses key aspects.
- 0.1-0.3 = The answer is tangentially related or largely incomplete.
- 0.0 = The answer is completely irrelevant or does not address the question.

Output ONLY a JSON object in this exact format:
{{"score": <float between 0.0 and 1.0>, "reasoning": "<detailed explanation>"}}

Do not include any markdown formatting, preamble, or text outside the JSON object."""

    return _call_judge(prompt, client)


def judge_context_precision(
    question: str,
    answer: str,
    retrieved_chunks: list[str],
    ground_truth_answer: str,
    ground_truth_chunk_ids: list[str],
    retrieved_chunk_ids: list[str],
    client: Groq,
) -> dict:
    context_text = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""You are an expert evaluator assessing CONTEXT PRECISION.
Context precision measures whether the retrieved chunks were genuinely useful and relevant, or if they contained noisy/irrelevant junk.

QUESTION: {question}

RETRIEVED CHUNKS:
{context_text}

RETRIEVED CHUNK IDs: {retrieved_chunk_ids}
GROUND TRUTH CHUNK IDs: {ground_truth_chunk_ids}

Evaluate whether the retrieved chunks are relevant and useful for answering the question.
- 1.0 = All retrieved chunks are highly relevant and necessary for answering the question.
- 0.7-0.9 = Most chunks are relevant, but one or two contain minor noise.
- 0.4-0.6 = Roughly half the chunks are relevant; significant noise is present.
- 0.1-0.3 = Most chunks are irrelevant or useless for the question.
- 0.0 = All retrieved chunks are completely irrelevant junk.

Output ONLY a JSON object in this exact format:
{{"score": <float between 0.0 and 1.0>, "reasoning": "<detailed explanation>"}}

Do not include any markdown formatting, preamble, or text outside the JSON object."""

    return _call_judge(prompt, client)


def judge_context_recall(
    question: str,
    answer: str,
    retrieved_chunks: list[str],
    ground_truth_answer: str,
    ground_truth_chunk_ids: list[str],
    retrieved_chunk_ids: list[str],
    client: Groq,
) -> dict:
    context_text = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""You are an expert evaluator assessing CONTEXT RECALL.
Context recall measures whether the retrieval step surfaced ALL the chunks needed to fully answer the question.

QUESTION: {question}

RETRIEVED CHUNKS:
{context_text}

RETRIEVED CHUNK IDs: {retrieved_chunk_ids}
GROUND TRUTH CHUNK IDs: {ground_truth_chunk_ids}

Evaluate whether the retrieved chunks contain ALL the information necessary to answer the question fully.
Compare the retrieved chunk IDs against the ground truth chunk IDs, and assess the content coverage.
- 1.0 = All ground truth chunks were retrieved; the retrieved content is fully sufficient.
- 0.7-0.9 = Most critical chunks were retrieved; minor information may be missing but the answer is still largely achievable.
- 0.4-0.6 = Some important chunks are missing; the retrieved content is incomplete.
- 0.1-0.3 = Most critical chunks are missing; the retrieved content is insufficient.
- 0.0 = None of the necessary chunks were retrieved.

Output ONLY a JSON object in this exact format:
{{"score": <float between 0.0 and 1.0>, "reasoning": "<detailed explanation>"}}

Do not include any markdown formatting, preamble, or text outside the JSON object."""

    return _call_judge(prompt, client)
