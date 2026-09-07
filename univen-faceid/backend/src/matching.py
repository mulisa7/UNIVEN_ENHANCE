"""Team 3 — matching & recognition engine.

Compares a face embedding against a set of stored embeddings using cosine
similarity, and picks the best match above a threshold (or reports no match).
Two thresholds are used by callers: a stricter one to refuse duplicate
enrollments, and a more permissive tunable one for live recognition.
"""

import os

import numpy as np

RECOGNITION_THRESHOLD = float(os.environ.get("MATCH_THRESHOLD", "0.85"))
DUPLICATE_THRESHOLD = float(os.environ.get("DUPLICATE_THRESHOLD", "0.92"))


def cosine_similarity(a, b) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def find_best_match(embedding, candidates, threshold):
    """`candidates` is a list of {"id", "name", "age", "embedding"} dicts.
    Returns (best_candidate_or_None, score)."""
    best = None
    best_score = -1.0
    for candidate in candidates:
        score = cosine_similarity(embedding, candidate["embedding"])
        if score > best_score:
            best_score = score
            best = candidate
    if best is not None and best_score >= threshold:
        return best, best_score
    return None, best_score if best is not None else 0.0


def is_duplicate(embedding, candidates) -> bool:
    match, _ = find_best_match(embedding, candidates, DUPLICATE_THRESHOLD)
    return match is not None
