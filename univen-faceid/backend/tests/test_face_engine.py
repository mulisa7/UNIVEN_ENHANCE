import numpy as np

import face_engine
from conftest import face_like_image

EXPLICIT_BOX = (60, 40, 180, 220)  # x, y, w, h — large enough to contain the synthetic face


def test_embed_face_is_deterministic():
    img = face_like_image()
    v1 = face_engine.embed_face(img, box=EXPLICIT_BOX)
    v2 = face_engine.embed_face(img, box=EXPLICIT_BOX)
    assert np.allclose(v1, v2)


def test_embed_face_fixed_length_and_normalized():
    img = face_like_image()
    vec = face_engine.embed_face(img, box=EXPLICIT_BOX)
    expected_len = face_engine.GRID[0] * face_engine.GRID[1] * 256
    assert vec.shape == (expected_len,)
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-6


def test_embed_face_similar_for_small_shift():
    a = face_engine.embed_face(face_like_image(), box=EXPLICIT_BOX)
    b = face_engine.embed_face(face_like_image(shift_x=2, shift_y=1), box=EXPLICIT_BOX)
    similarity = float(np.dot(a, b))  # both are L2-normalized
    assert similarity > 0.8


def _random_textured_image(seed, size=(300, 300)):
    # A flat/solid-color image degenerately collapses LBP codes to a single
    # value (every pixel "equals" its neighbors), which coincidentally
    # matches the flat background regions in face_like_image() and produces
    # a misleadingly high similarity — not representative of two genuinely
    # different faces. Random texture avoids that degenerate case.
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=(size[1], size[0], 3), dtype=np.uint8)


def test_embed_face_differs_for_different_pattern():
    a = face_engine.embed_face(_random_textured_image(1), box=EXPLICIT_BOX)
    b = face_engine.embed_face(_random_textured_image(2), box=EXPLICIT_BOX)
    similarity = float(np.dot(a, b))
    assert similarity < 0.9


def test_detect_faces_returns_list_without_error():
    img = face_like_image()
    boxes = face_engine.detect_faces(img)
    assert isinstance(boxes, list)


def test_average_embeddings_is_normalized():
    img = face_like_image()
    vecs = [face_engine.embed_face(img, box=EXPLICIT_BOX) for _ in range(3)]
    avg = face_engine.average_embeddings(vecs)
    assert abs(np.linalg.norm(avg) - 1.0) < 1e-6
