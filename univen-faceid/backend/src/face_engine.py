"""Team 1 — face detection & embedding engine.

Offline-only implementation: Haar-cascade detection and a grid-based Local
Binary Pattern (LBP) histogram as the face "embedding". Both ship inside
opencv-python already, so there is no model file to download and no native
build toolchain (dlib) required. Accuracy is well below a trained deep
embedding model (ArcFace/FaceNet) — this is a stand-in that satisfies the same
interface (`embed_face` -> fixed-length vector, compared by cosine similarity)
so it can be swapped out later without touching callers.
"""

import cv2
import numpy as np

FACE_SIZE = (92, 112)  # width, height
GRID = (8, 8)
LBP_RADIUS = 1

_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def decode_image(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image")
    return img


def detect_faces(image: np.ndarray):
    """Returns a list of (x, y, w, h) bounding boxes, largest first."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    boxes = _cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )
    return sorted(boxes, key=lambda b: b[2] * b[3], reverse=True)


def _lbp_image(gray: np.ndarray) -> np.ndarray:
    h, w = gray.shape
    padded = np.pad(gray, LBP_RADIUS, mode="edge").astype(np.int16)
    center = padded[LBP_RADIUS : LBP_RADIUS + h, LBP_RADIUS : LBP_RADIUS + w]
    offsets = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
    code = np.zeros((h, w), dtype=np.uint8)
    for bit, (dy, dx) in enumerate(offsets):
        neighbor = padded[
            LBP_RADIUS + dy : LBP_RADIUS + dy + h, LBP_RADIUS + dx : LBP_RADIUS + dx + w
        ]
        code |= ((neighbor >= center).astype(np.uint8)) << bit
    return code


def _face_vector(face_gray: np.ndarray) -> np.ndarray:
    face_gray = cv2.equalizeHist(face_gray)
    lbp = _lbp_image(face_gray)
    gh, gw = GRID
    h, w = lbp.shape
    cell_h, cell_w = h // gh, w // gw
    hist = []
    for gy in range(gh):
        for gx in range(gw):
            cell = lbp[
                gy * cell_h : (gy + 1) * cell_h, gx * cell_w : (gx + 1) * cell_w
            ]
            counts, _ = np.histogram(cell, bins=256, range=(0, 256))
            hist.append(counts)
    vec = np.concatenate(hist).astype(np.float64)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def embed_face(image: np.ndarray, box=None) -> np.ndarray:
    """Crops to `box` (or the largest detected face if None) and returns a
    fixed-length, L2-normalized embedding vector."""
    if box is None:
        boxes = detect_faces(image)
        if not boxes:
            raise ValueError("No face detected")
        box = boxes[0]
    x, y, w, h = box
    face = image[y : y + h, x : x + w]
    face = cv2.resize(face, FACE_SIZE)
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    return _face_vector(gray)


def average_embeddings(vectors) -> np.ndarray:
    avg = np.mean(np.stack(vectors), axis=0)
    norm = np.linalg.norm(avg)
    return avg / norm if norm > 0 else avg
