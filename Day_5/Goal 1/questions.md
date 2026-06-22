## Project Evaluation & Code Review — Day 5: Vector Search & Embeddings

### Q1: What is an embedding, and why do semantically similar texts produce similar embedding vectors?
**Answer:**
_Write your answer here..._

### Q2: Why did this project choose 512-token chunks, and what problem does the 64-token overlap between consecutive chunks solve?
**Answer:**
_Write your answer here..._

### Q3: What is the difference between the RETRIEVAL_DOCUMENT and RETRIEVAL_QUERY task types in the Gemini embedding API, and why does this project use a different one for indexing versus querying?
**Answer:**
_Write your answer here..._

### Q4: Why does DOT_PRODUCT_DISTANCE produce the same ranking as cosine similarity for this project's embeddings? Show the math.
**Answer:**
_Write your answer here..._

### Q5: What does the Vertex AI Index resource represent, what does the IndexEndpoint resource represent, and why does Vertex AI require both rather than just one?
**Answer:**
_Write your answer here..._

### Q6: How does the Namespace `restricts` filter mechanism work inside Vertex AI Vector Search at query time, and why is filtering done this way instead of retrieving everything and filtering afterward?
**Answer:**
_Write your answer here..._

### Q7: What are the tradeoffs between Approximate Nearest Neighbor (ANN) search and exact K-Nearest-Neighbors (KNN)? Describe a scenario where you would choose exact KNN despite its higher cost.
**Answer:**
_Write your answer here..._

### Q8: Why does using the same embedding task_type for both indexing and querying matter for the dot-product score distribution returned by the index?
**Answer:**
_Write your answer here..._

### Q9: Suppose Google releases a new version of the Gemini embedding model after you've already indexed 200 papers with the old version. How would you detect that embedding drift has occurred, and how would you handle migrating the index?
**Answer:**
_Write your answer here..._

### Q10: Design a re-ranking layer to sit between Vertex AI's retrieval step and Groq's synthesis step. What signals would you use to re-rank the initial top-K candidates, and why does high retrieval recall not guarantee high final answer quality?
**Answer:**
_Write your answer here..._
