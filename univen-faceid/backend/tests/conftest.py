import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
import pytest


def face_like_image(shift_x=0, shift_y=0, size=(300, 300)) -> np.ndarray:
    """Draws a simple synthetic face (oval + two eyes + a mouth) so the Haar
    cascade has a plausible chance of detecting it, without needing a real
    photo. Not photorealistic — used only to exercise the pipeline end to
    end deterministically."""
    import cv2

    img = np.full((size[1], size[0], 3), 200, dtype=np.uint8)
    cx, cy = size[0] // 2 + shift_x, size[1] // 2 + shift_y
    cv2.ellipse(img, (cx, cy), (90, 120), 0, 0, 360, (180, 170, 160), -1)
    cv2.circle(img, (cx - 35, cy - 30), 12, (30, 30, 30), -1)
    cv2.circle(img, (cx + 35, cy - 30), 12, (30, 30, 30), -1)
    cv2.ellipse(img, (cx, cy + 50), (40, 15), 0, 0, 180, (60, 40, 40), 3)
    return img


@pytest.fixture
def sample_face():
    return face_like_image()


@pytest.fixture
def sample_face_shifted():
    return face_like_image(shift_x=5, shift_y=3)


def database_available() -> bool:
    import psycopg2

    try:
        conn = psycopg2.connect(
            os.environ.get(
                "DATABASE_URL", "postgresql://faceid:faceid@localhost:5433/faceid"
            ),
            connect_timeout=2,
        )
        conn.close()
        return True
    except Exception:
        return False
