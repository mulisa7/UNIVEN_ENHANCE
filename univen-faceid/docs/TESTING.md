# Testing (Team 6)

## Automated tests

Run from `backend/`:

```bash
pytest
```

- `tests/test_face_engine.py` — embedding determinism and stability, using
  synthetically drawn face-like images (no real photos needed).
- `tests/test_matching.py` — cosine similarity, threshold, and duplicate
  detection logic on fabricated embedding vectors.
- `tests/test_api.py` — full API behavior via `TestClient`. These
  DB-touching tests are skipped automatically if Postgres isn't reachable —
  start it with `docker compose up -d db` (from the project root) to run
  them for real.

Run `python backend/benchmark/benchmark_detection.py <folder>` against a
folder of sample face photos to measure Team 1's detection hit-rate and
throughput.

## Manual test matrix

The automated tests can't exercise a real camera or real faces. Before
trusting this system with real enrollments, manually walk through this
matrix with a small, consenting group of testers (e.g. the project teams
themselves):

| Condition | What to check |
|---|---|
| Bright, even lighting | Enrollment and recognition both succeed |
| Dim / backlit lighting | Detection may fail — confirm the UI shows a clear error rather than a silent failure |
| Straight-on angle | Baseline recognition accuracy |
| Slight left/right/up/down angle | Recognition still succeeds (the 3-angle enrollment capture is meant to help here) |
| Glasses | Enroll with glasses, recognize with and without — check both work |
| Hat / hood / mask | Detection should fail gracefully rather than mis-embed a non-face region |
| Two visually similar people (e.g. siblings) | Confirm they are NOT cross-matched; if they are, `MATCH_THRESHOLD` needs tightening |
| Re-enrolling the same person | `POST /enroll` should return 409 (duplicate), not create a second record |
| Enrolling with an empty name / age 0 | `POST /enroll` should return 400 with a clear message |
| Deleting a record via the Privacy tab | Record disappears from `GET /people` immediately and permanently |
| Growing the enrolled database | Periodically re-check false-match rate as more people enroll — the guide notes accuracy naturally drops as the database grows, so `MATCH_THRESHOLD` may need retuning over time |

Log results (pass/fail + notes) for each row before treating the system as
ready for anything beyond a classroom demo.
