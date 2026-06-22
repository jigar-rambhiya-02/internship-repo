import pytest
from hybrid.rrf import compute_rrf

def test_rrf_standard_merging_behavior():
    """
    Case 1: Validates combining predictable overlapping values.
    Chunk 'doc_A' occupies position #1 in Dense, position #2 in Sparse.
    RRF Score Arithmetic calculation with k=60:
    Dense: 1 / (60 + 1) = 1 / 61 = 0.01639344
    BM25:  1 / (60 + 2) = 1 / 62 = 0.01612903
    Expected Combined Sum total = 0.03252247
    """
    dense_mock = [("doc_A", 1), ("doc_B", 2)]
    bm25_mock = [("doc_B", 1), ("doc_A", 2)]
    
    output = compute_rrf(dense_mock, bm25_mock, k=60)
    scores_dict = dict(output)
    
    expected_doc_a = (1.0 / 61) + (1.0 / 62)
    expected_doc_b = (1.0 / 62) + (1.0 / 61)
    
    assert "doc_A" in scores_dict
    assert "doc_B" in scores_dict
    assert pytest.approx(scores_dict["doc_A"], rel=1e-5) == expected_doc_a
    assert pytest.approx(scores_dict["doc_B"], rel=1e-5) == expected_doc_b

def test_rrf_zero_overlap_disjoint_lists():
    """
    Case 2: Ensures that documents appearing exclusively in one list 
    are integrated correctly without causing null pointer errors.
    """
    dense_mock = [("doc_vector_only", 1)]
    bm25_mock = [("doc_keyword_only", 5)]
    
    output = compute_rrf(dense_mock, bm25_mock, k=60)
    scores_dict = dict(output)
    
    assert scores_dict["doc_vector_only"] == pytest.approx(1.0 / 61)
    assert scores_dict["doc_keyword_only"] == pytest.approx(1.0 / 65)
    assert output[0][0] == "doc_vector_only" # Due to higher RRF score profile

def test_rrf_empty_input_handling():
    """
    Case 3: Confirms the function handles completely empty candidate arrays gracefully.
    """
    output = compute_rrf([], [], k=60)
    assert output == []

