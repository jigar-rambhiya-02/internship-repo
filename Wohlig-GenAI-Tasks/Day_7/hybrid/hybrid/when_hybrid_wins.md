# Findings Document: Empirical Analysis of Hybrid Retrieval Performance

## Query-Type Breakdown Metrics Summary Table
The table below represents the average retrieval accuracy across individual retrieval modalities based on performance metrics compiled inside `hybrid/results.csv`.

| Evaluation Query Profile Type | Dense-Only (Recall@5) | BM25-Only (Recall@5) | Hybrid RRF Engine (Recall@5) |
| :--- | :--- | :--- | :--- |
| **Semantic Queries** (30 cases) | 1.00 | 0.33 | 1.00 |
| **Keyword-Heavy Queries** (5 cases) | 0.20 | 1.00 | 1.00 |
| **Mixed Queries** (5 cases) | 0.60 | 0.80 | 1.00 |

---

## Technical Performance Analysis

### Scenario 1: When Hybrid Retrieval Outperforms Vector-Only Search
Vector search maps input queries to semantic concepts based on training distributions. However, it fails when processing queries that include precise alphanumeric character identifiers. For example, in a query like *"explain policy ABC-2024-117 notification periods"*, a dense vector encoder treats the specific token strings as minor noise relative to the surrounding semantic structure ("explain notification periods"). This causes the model to surf through general insurance documents, frequently missing the exact contract fragment required. 

BM25 resolves this by evaluating term match density. Combining these methods via Reciprocal Rank Fusion ensures that any document containing exact terms (like *ABC-2024-117* or *clause 8.2.1*) receives a significant rank boost, ensuring that critical specific documents are surfaced within the top 5 results even when their semantic match score is low.

### Scenario 2: When Hybrid Search is Overkill
In environments with highly homogenous document formats that lack specific alphanumeric codes—such as general creative content libraries, abstract thematic research repositories, or customer sentiment records—hybrid search provides negligible accuracy improvements. 

In these cases, running dual extraction branches incurs unnecessary compute costs, doubled indexing footprints, and increased engineering complexity, since dense vector operations alone can effectively navigate these conversational document frameworks.

---

## Strategic Client Recommendations

### Client Scenario A: Multi-National Enterprise Legal Department
* **Objective**: Search across vendor agreements, non-disclosure templates, and corporate governance charters.
* **Core Challenge**: Queries focus on identifying legal liabilities tied to specific subsections, such as *"What are the liabilities outlined in clause 8.2.1?"*.
* **Recommendation**: **Hybrid Retrieval Engine**. Vector search alone cannot differentiate between "clause 8.2.1" and "clause 8.2.2" in dense embeddings space, while BM25 handles exact match constraints perfectly.

### Client Scenario B: High-Volume Customer Support FAQ Chatbot
* **Objective**: Match natural language consumer queries to a curated collection of clear help center articles.
* **Core Challenge**: Users ask highly varied questions using conversational language, slang, and synonyms (e.g., *"My account is locked"* vs. *"I cannot access my dashboard"*).
* **Recommendation**: **Dense-Only Vector Search**. The problem space is entirely semantic, meaning keyword matching will fail to resolve conversational variation.

### Client Scenario C: Global Regulatory & Tariff Compliance Operations
* **Objective**: Audit import logs against official tariff books to confirm customs compliance.
* **Core Challenge**: Inquiries combine conversational descriptions with precise numeric codes, such as *"What is the import duty for genuine rubber-soled footwear under HS code 6403?"*.
* **Recommendation**: **Hybrid Retrieval Engine**. This use case requires a balance of semantic context processing and exact keyword matching, making it a perfect fit for a hybrid approach.

