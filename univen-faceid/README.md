# Univen FaceID

A face-enrollment and recognition system. A person registers once with their
name, age, and three face captures; from then on, a live camera view can
recognize them and display their name and age automatically.

Built out from the Univen Enhance initiative's 6-team project guide — see
`docs/ARCHITECTURE.md` for the team-to-file map and `docs/PRIVACY.md` for the
POPIA compliance notes.

## Running it

**1. Start the database**

```bash
docker compose up -d db
```

(Requires Docker Desktop running. `docker compose up -d` instead will also
build and start the backend in a container — see below for the alternative
of running the backend locally with hot reload.)

Postgres is exposed on host port **5433**, not the default 5432 — this
avoids clashing with a native PostgreSQL install some machines already have
running on 5432. `backend/.env.example` already points at 5433; only change
this if your own setup differs.

**2. Apply migrations**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python src/migrate.py
```

**3. Run the backend**

```bash
cd backend
uvicorn main:app --reload --app-dir src
```

The API is now at `http://localhost:8000` (docs at `/docs`).

**4. Run the frontend**

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open the printed local URL, allow camera access, and enroll a face.

## Running tests

```bash
cd backend
pytest
```

Embedding/matching unit tests run with no setup. API tests need Postgres
running (step 1 above) — they skip automatically otherwise.

## Tech choices vs. the original guide

- **Face embedding**: offline-only (OpenCV Haar cascade + LBP histogram)
  instead of dlib/`face_recognition` or a downloaded ONNX model, so the
  project installs cleanly with zero native build tools and zero network
  downloads. Lower accuracy than a real deep model — see the "Known
  limitation" note in `docs/ARCHITECTURE.md` for the swap-out seam.
- **Database**: PostgreSQL via Docker, as the guide specifies.
