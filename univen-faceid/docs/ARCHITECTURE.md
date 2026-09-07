# Architecture

## System overview

```
                 ┌──────────────────────────┐
                 │   Frontend (React/Vite)  │
                 │  Team 2, 5, 6 components │
                 └────────────┬─────────────┘
                              │ HTTP (multipart form-data)
                              ▼
                 ┌──────────────────────────┐
                 │   Backend (FastAPI)      │
                 │   Team 4 — routes/*.py   │
                 └───────┬──────────┬───────┘
                         │          │
          ┌──────────────┘          └───────────────┐
          ▼                                         ▼
┌──────────────────────┐               ┌──────────────────────────┐
│ face_engine.py        │               │ matching.py               │
│ Team 1 — detect +      │──embeddings──▶│ Team 3 — cosine similarity │
│ embed a face           │               │ + threshold decision       │
└──────────────────────┘               └─────────────┬────────────┘
                                                       │
                                                       ▼
                                          ┌──────────────────────────┐
                                          │  PostgreSQL (Docker)      │
                                          │  people(id, name, age,    │
                                          │  embedding, created_at)   │
                                          └──────────────────────────┘
```

## Team-to-file map

| Team | Scope | Files |
|---|---|---|
| 1 | Face detection & embedding | `backend/src/face_engine.py`, `backend/benchmark/benchmark_detection.py` |
| 2 | Enrollment system | `frontend/src/components/EnrollmentForm.jsx`, `backend/src/routes/enroll.py` |
| 3 | Matching & recognition | `backend/src/matching.py`, `backend/src/routes/recognize.py` |
| 4 | Database & backend API | `backend/migrations/`, `backend/src/db.py`, `backend/src/main.py`, `backend/src/schemas.py`, `backend/src/routes/people.py` |
| 5 | Live recognition frontend | `frontend/src/components/LiveRecognition.jsx` |
| 6 | Privacy, ethics & testing | `frontend/src/components/ConsentNotice.jsx`, `frontend/src/components/PrivacyPanel.jsx`, `docs/PRIVACY.md`, `docs/TESTING.md` |

## Enrollment flow (matches the guide's 7 steps)

1. User types name + age into `EnrollmentForm`.
2. `ConsentNotice` is shown and must be accepted before the camera activates.
3. Camera captures 3 images: front, left, right.
4. Backend's `face_engine.embed_face` converts each image to a vector; the 3
   are averaged into one embedding (`face_engine.average_embeddings`).
5. `matching.is_duplicate` checks the new embedding against every stored
   embedding (using `DUPLICATE_THRESHOLD`) to reject re-enrollment.
6. The record (name, age, embedding) is inserted into `people`.
7. The frontend shows an on-screen success message.

## Recognition flow (matches the guide's 6 steps)

1–2. `LiveRecognition` grabs a frame from the live camera every ~1.5s (not
every frame, to save processing power).
3. The frame is sent to the backend as multipart form data.
4. `routes/recognize.py` calls `face_engine.embed_face` on the frame.
5. `matching.find_best_match` compares it to every stored embedding using
   cosine similarity.
6a. If the best score clears `MATCH_THRESHOLD`, the person's name and age are
returned and displayed.
6b. Otherwise the frontend shows "Unknown — not enrolled."

## Known limitation

Face detection/embedding (Team 1) is implemented with OpenCV Haar-cascade
detection and a hand-rolled LBP-histogram "embedding" — chosen deliberately
to avoid a dlib build toolchain or downloading model weights. It is
noticeably less accurate than a trained deep model (ArcFace/FaceNet via
`face_recognition` or an ONNX model). `face_engine.embed_face` is the single
seam to swap in a real model later without touching `matching.py` or any
route.
