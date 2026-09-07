# Privacy & Compliance (Team 6)

## Legal basis

Biometric data — including face images and face embeddings — is classified
as **special personal information** under South Africa's Protection of
Personal Information Act (POPIA). This system must not capture anyone's face
without their explicit, informed, opt-in consent.

## Consent

Shown to every user before their camera activates (see
`frontend/src/components/ConsentNotice.jsx`, and Step 2 of the enrollment
flow in `docs/ARCHITECTURE.md`):

> Univen FaceID will capture three images of your face (front, left, right)
> and convert them into a numeric representation ("embedding") used to
> recognize you later. This is treated as special personal information under
> South Africa's POPIA.
>
> - We store the embedding, not your raw photos.
> - Your name and age are stored alongside the embedding.
> - You can request deletion of your data at any time.
> - Your face data is only used to recognize you within this system.

Consent must be a standalone, informed action — it is never bundled into
unrelated terms of service, and is never assumed from prior use of the app.

## What is stored

| Field | Stored? | Notes |
|---|---|---|
| Raw face photos | No | Discarded client-side/server-side after embedding is computed; only the 3 captured blobs briefly exist in memory during the enrollment request. |
| Face embedding | Yes | A numeric vector — far harder to reverse into a usable photo than a raw image. Stored in the `people.embedding` column. |
| Name, age | Yes | Stored alongside the embedding in the same `people` row. |
| Recognition history | No | Recognition is stateless — a `/recognize` call is matched and returned; no log of who was seen when is kept. |

Raw embeddings are never included in any API response — `schemas.py`'s
response models (`PersonOut`, `EnrollResponse`, `RecognizeResponse`)
structurally exclude the `embedding` field, so this can't be broken by
accident in a route handler.

## Access & deletion

- Anyone can view the current enrolled list (name + age only, no embeddings)
  via `GET /people`, surfaced in the frontend's Privacy tab.
- Anyone can request permanent deletion of their own record via
  `DELETE /people/{id}` (also exposed as a button in the Privacy tab). This
  is a hard delete — the row, including the embedding, is removed
  immediately and is not recoverable.

## Rollout guidance

- Start testing with a small, consenting group (e.g. the project teams
  themselves) before enrolling the wider student body.
- Recognition accuracy naturally drops as the enrolled database grows — plan
  `MATCH_THRESHOLD` tuning (Team 3, see `backend/.env.example`) accordingly
  as more people are enrolled.
- Before any deployment past a classroom demo, add: audit logging of who
  accessed the `/people` and delete endpoints, an authentication layer (the
  current API has none — anyone reaching it can enroll, recognize, list, or
  delete), and a retention policy (e.g. auto-expire embeddings after a term
  ends).
