import json
import os
from pathlib import Path
from config.settings import CORPUS_DIR, GROQ_API_KEY, CHUNK_SIZE_TOKENS, OVERLAP_TOKENS, MAX_SEMANTIC_TOKENS
from utils.io_utils import load_corpus
from chunking.strategies import fixed_size, sentence_aware, semantic
from groq import Groq

client = Groq(api_key=GROQ_API_KEY)
corpus = load_corpus(CORPUS_DIR)
doc_ids = list(corpus.keys())[:50]

# Chunk all documents
chunks_by_strategy = {"fixed": {}, "sentence": {}, "semantic": {}}
for doc_id in doc_ids:
    text = corpus[doc_id]
    chunks_by_strategy["fixed"][doc_id] = fixed_size(text, doc_id, CHUNK_SIZE_TOKENS, OVERLAP_TOKENS)
    chunks_by_strategy["sentence"][doc_id] = sentence_aware(text, doc_id, CHUNK_SIZE_TOKENS)
    chunks_by_strategy["semantic"][doc_id] = semantic(text, doc_id, MAX_SEMANTIC_TOKENS)

def find_chunk_id(snippet, doc_id, strategy):
    for chunk in chunks_by_strategy[strategy].get(doc_id, []):
        if snippet in chunk["text"]:
            return chunk["chunk_id"]
    return None

questions = []
for i in range(25):
    doc_id = doc_ids[i % len(doc_ids)]
    text = corpus[doc_id]
    excerpt = text[:3000]
    prompt = f"""Document: {excerpt}
Generate a factual question and the exact answer snippet (10-50 words) from this document.
Return JSON: {{"question": "...", "answer_snippet": "...", "doc_id": "{doc_id}"}}"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    data = json.loads(response.choices[0].message.content)
    snippet = data["answer_snippet"]
    gt = {}
    for strat in ["fixed", "sentence", "semantic"]:
        cid = find_chunk_id(snippet, doc_id, strat)
        if cid:
            gt[strat] = [cid]
    questions.append({
        "question_id": f"q{i+1:03d}",
        "question": data["question"],
        "ground_truth_chunk_ids": gt,
        "notes": f"Snippet: {snippet[:100]}"
    })
    print(f"Generated {i+1}/25")

with open("chunking/test_set.jsonl", "w") as f:
    for q in questions:
        f.write(json.dumps(q) + "\n")
print("Done")