from fastapi import APIRouter, File, HTTPException, UploadFile

import db
import face_engine
import matching
from schemas import PersonOut, RecognizeResponse

router = APIRouter()


@router.post("/recognize", response_model=RecognizeResponse)
async def recognize(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    content = await image.read()
    decoded = face_engine.decode_image(content)
    try:
        embedding = face_engine.embed_face(decoded)
    except ValueError:
        return RecognizeResponse(matched=False, person=None, confidence=0.0)

    candidates = db.query(
        "SELECT id, name, age, embedding, created_at FROM people", fetch=True
    )
    match, score = matching.find_best_match(
        embedding, candidates, matching.RECOGNITION_THRESHOLD
    )
    if match is None:
        return RecognizeResponse(matched=False, person=None, confidence=score)

    person = PersonOut(
        id=match["id"], name=match["name"], age=match["age"], created_at=match["created_at"]
    )
    return RecognizeResponse(matched=True, person=person, confidence=score)
