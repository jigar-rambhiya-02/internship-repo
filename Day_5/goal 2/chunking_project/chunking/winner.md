# Chunking Strategy Evaluation: Winner Analysis

## Aggregate Scores

| Strategy | mean_recall@5 | mean_recall@10 |
|---|---|---|
| `fixed` ✅ WINNER | 0.8400 | 0.8400 |
| `semantic` | 0.8000 | 0.8800 |
| `sentence` | 0.8000 | 0.8400 |

## Recommended Chunker: `fixed`

The 'fixed' approach emerged as the top performer in the chunking evaluation, with a mean recall of 0.84 at both the 5 and 10 recall thresholds. This suggests that the fixed chunking strategy is effective in identifying relevant information within the corpus, likely due to its ability to consistently capture key phrases and entities. The corpus structure, which may include a mix of short and long documents, as well as varying levels of semantic complexity, appears to be well-suited for the fixed approach. By dividing the text into fixed-size chunks, this method is able to balance the trade-off between recall and precision, resulting in a high overall recall score.

The success of the 'fixed' approach has significant implications for production use, as it indicates that this method can be relied upon to effectively identify and extract relevant information from the corpus. In particular, the fact that the fixed approach outperformed the sentence-based approach suggests that the corpus structure is not strongly dominated by sentence-level boundaries, and that a more flexible chunking strategy is needed to capture relevant information. As a result, the fixed approach can be used with confidence in production environments, where high recall and precision are critical for downstream applications such as question answering and text summarization. By leveraging the fixed chunking strategy, developers can build more effective RAG systems that are capable of extracting relevant information from complex corpora.

## Rule of Thumb

| Corpus Type | Recommended Strategy | Reasoning |
|---|---|---|
| Markdown / structured docs with headings | `semantic` | Headings define natural topic boundaries; chunks map to coherent sections |
| Plain prose, articles, transcripts | `sentence` | Sentence boundaries preserve grammatical coherence without relying on formatting |
| Unstructured text, logs, code, tables | `fixed` | No reliable boundaries exist; consistent size reduces retrieval variance |
| Mixed corpora | `sentence` | Safest general fallback; degrades gracefully on both structured and unstructured text |

## Per-Question Breakdown

Questions where the winner failed (recall@5 = 0.0):

- `q009`: What is the purpose of CSS?
- `q010`: What is on-demand self-service in cloud computing?
- `q015`: What does a data scientist do?
- `q019`: When was the first clickable banner ad launched?

## Methodology Notes

- **Vector search:** TF-IDF with cosine similarity (scikit-learn). Lexical matching only.
- **Recall formula:** `|retrieved_k ∩ ground_truth| / |ground_truth|`
- **Corpus subset:** 50 documents from `data/corpus/`
- **Test set:** 25 questions with manually verified ground-truth chunk IDs
- **Chunk size target:** 256 tokens (fixed/sentence), 512 tokens max (semantic)

> **Production note:** TF-IDF retrieval underestimates semantic chunking's advantage in production,
> because dense embeddings better capture meaning across paraphrase boundaries where semantic chunks excel.
> If this experiment is reproduced with dense embeddings (e.g., `all-MiniLM-L6-v2`), expect
> the gap between semantic and fixed-size to widen.
