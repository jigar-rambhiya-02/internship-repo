import json
import random
from config.settings import CORPUS_DIR, CHUNK_SIZE_TOKENS, OVERLAP_TOKENS, MAX_SEMANTIC_TOKENS
from utils.io_utils import load_corpus
from chunking.strategies import fixed_size, sentence_aware, semantic
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
corpus = load_corpus(CORPUS_DIR)
doc_ids = list(corpus.keys())[:50]

# Store all chunks for each strategy (for fast lookup)
chunks_by_strategy = {"fixed": {}, "sentence": {}, "semantic": {}}
for doc_id in doc_ids:
    text = corpus[doc_id]
    chunks_by_strategy["fixed"][doc_id] = fixed_size(text, doc_id, CHUNK_SIZE_TOKENS, OVERLAP_TOKENS)
    chunks_by_strategy["sentence"][doc_id] = sentence_aware(text, doc_id, CHUNK_SIZE_TOKENS)
    chunks_by_strategy["semantic"][doc_id] = semantic(text, doc_id, MAX_SEMANTIC_TOKENS)

def find_chunk_for_snippet(snippet, doc_id, strategy):
    for chunk in chunks_by_strategy[strategy][doc_id]:
        if snippet in chunk["text"]:
            return chunk["chunk_id"]
    return None

questions = []
used_snippets = set()

for i in range(25):
    # Randomly pick a document
    doc_id = random.choice(doc_ids)
    # Pick a random chunk from fixed-size (just to get a candidate sentence)
    fixed_chunks = chunks_by_strategy["fixed"][doc_id]
    if not fixed_chunks:
        continue
    chunk = random.choice(fixed_chunks)
    sentences = chunk["text"].split(". ")
    if len(sentences) < 2:
        continue
    candidate_sentence = sentences[0] + "."  # first sentence of the chunk
    if len(candidate_sentence) < 20 or candidate_sentence in used_snippets:
        continue
    used_snippets.add(candidate_sentence)
    
    # Verify which strategies contain this exact sentence
    gt = {}
    for strat in ["fixed", "sentence", "semantic"]:
        cid = find_chunk_for_snippet(candidate_sentence, doc_id, strat)
        if cid:
            gt[strat] = [cid]
    if len(gt) == 0:
        continue
    
    # Use Groq to generate a question from the sentence
    prompt = f"Given the following sentence: '{candidate_sentence}'\nGenerate a natural question that this sentence answers. Return only the question text."
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    question_text = response.choices[0].message.content.strip()
    
    questions.append({
        "question_id": f"q{i+1:03d}",
        "question": question_text,
        "ground_truth_chunk_ids": gt,
        "notes": f"Snippet: {candidate_sentence[:100]}"
    })
    print(f"Generated {len(questions)} questions...")

# Save to test_set.jsonl
import json
from pathlib import Path
test_path = Path("chunking/test_set.jsonl")
test_path.parent.mkdir(parents=True, exist_ok=True)
with open(test_path, "w", encoding="utf-8") as f:
    for q in questions:
        f.write(json.dumps(q) + "\n")
print(f"Saved {len(questions)} questions to {test_path}")
