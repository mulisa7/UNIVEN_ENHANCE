import numpy as np

import matching


def _vec(seed, dim=32):
    rng = np.random.default_rng(seed)
    v = rng.normal(size=dim)
    return v / np.linalg.norm(v)


def test_cosine_similarity_identical_is_one():
    v = _vec(1)
    assert abs(matching.cosine_similarity(v, v) - 1.0) < 1e-9


def test_cosine_similarity_orthogonal_is_zero():
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert abs(matching.cosine_similarity(a, b)) < 1e-9


def test_find_best_match_returns_none_below_threshold():
    embedding = _vec(1)
    candidates = [{"id": 1, "name": "A", "age": 20, "embedding": _vec(2)}]
    match, score = matching.find_best_match(embedding, candidates, threshold=0.9)
    assert match is None


def test_find_best_match_returns_candidate_above_threshold():
    embedding = _vec(1)
    candidates = [
        {"id": 1, "name": "A", "age": 20, "embedding": _vec(2)},
        {"id": 2, "name": "B", "age": 30, "embedding": embedding.tolist()},
    ]
    match, score = matching.find_best_match(embedding, candidates, threshold=0.9)
    assert match is not None
    assert match["id"] == 2
    assert score > 0.9


def test_find_best_match_empty_candidates():
    match, score = matching.find_best_match(_vec(1), [], threshold=0.9)
    assert match is None
    assert score == 0.0


def test_is_duplicate_true_when_near_identical():
    embedding = _vec(5)
    candidates = [{"id": 1, "name": "A", "age": 20, "embedding": embedding.tolist()}]
    assert matching.is_duplicate(embedding, candidates) is True


def test_is_duplicate_false_when_different():
    candidates = [{"id": 1, "name": "A", "age": 20, "embedding": _vec(7).tolist()}]
    assert matching.is_duplicate(_vec(8), candidates) is False
