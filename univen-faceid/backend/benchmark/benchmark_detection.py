"""Team 1 — benchmarks detection speed and hit-rate over a folder of images.

Usage: python benchmark_detection.py path/to/image/folder
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import cv2  # noqa: E402

import face_engine  # noqa: E402

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def run(folder: str):
    paths = [p for p in Path(folder).iterdir() if p.suffix.lower() in IMAGE_EXTS]
    if not paths:
        print(f"No images found in {folder}")
        return

    detected = 0
    total_time = 0.0
    for path in paths:
        img = cv2.imread(str(path))
        if img is None:
            continue
        start = time.perf_counter()
        boxes = face_engine.detect_faces(img)
        total_time += time.perf_counter() - start
        if len(boxes) > 0:
            detected += 1

    n = len(paths)
    print(f"Images: {n}")
    print(f"Faces detected in: {detected}/{n} ({100 * detected / n:.1f}%)")
    print(f"Avg detection time: {1000 * total_time / n:.1f} ms/image")
    print(f"Throughput: {n / total_time:.1f} images/sec")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python benchmark_detection.py path/to/image/folder")
        sys.exit(1)
    run(sys.argv[1])
