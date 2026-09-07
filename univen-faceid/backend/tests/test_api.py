import io

import cv2
import pytest
from fastapi.testclient import TestClient

from conftest import database_available, face_like_image

pytestmark = pytest.mark.skipif(
    not database_available(),
    reason="Postgres is not reachable (start it with `docker compose up -d db`)",
)


@pytest.fixture
def client():
    from main import app

    return TestClient(app)


def _jpeg_bytes(img) -> bytes:
    ok, buf = cv2.imencode(".jpg", img)
    assert ok
    return buf.tobytes()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_enroll_rejects_wrong_image_count(client):
    files = [("images", ("a.jpg", io.BytesIO(_jpeg_bytes(face_like_image())), "image/jpeg"))]
    res = client.post("/enroll", data={"name": "Test", "age": 20}, files=files)
    assert res.status_code == 400


def test_enroll_rejects_bad_age(client):
    files = [
        ("images", (f"{i}.jpg", io.BytesIO(_jpeg_bytes(face_like_image())), "image/jpeg"))
        for i in range(3)
    ]
    res = client.post("/enroll", data={"name": "Test", "age": 0}, files=files)
    assert res.status_code == 400


def test_recognize_returns_unmatched_for_unenrolled_face(client):
    img = face_like_image(shift_x=99, shift_y=99)
    files = {"image": ("f.jpg", io.BytesIO(_jpeg_bytes(img)), "image/jpeg")}
    res = client.post("/recognize", files=files)
    assert res.status_code == 200
    assert res.json()["matched"] is False


def test_people_list_excludes_embedding(client):
    res = client.get("/people")
    assert res.status_code == 200
    for person in res.json():
        assert "embedding" not in person


def test_delete_nonexistent_person_returns_404(client):
    res = client.delete("/people/999999999")
    assert res.status_code == 404
