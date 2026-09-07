import json
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

import db
import face_engine
import matching
from schemas import EnrollResponse, PersonOut

router = APIRouter()


def _all_people():
    return db.query("SELECT id, name, age, embedding FROM people", fetch=True)


@router.post("/enroll", response_model=EnrollResponse)
async def enroll(
    name: str = Form(...),
    age: int = Form(...),
    images: List[UploadFile] = File(...),
):
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    if age <= 0:
        raise HTTPException(status_code=400, detail="Age must be a positive integer")
    if len(images) != 3:
        raise HTTPException(status_code=400, detail="Exactly 3 images required")

    embeddings = []
    for img in images:
        if not img.content_type or not img.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {img.filename}")
        content = await img.read()
        decoded = face_engine.decode_image(content)
        try:
            embeddings.append(face_engine.embed_face(decoded))
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"No face detected in {img.filename}"
            )

    avg_embedding = face_engine.average_embeddings(embeddings)

    existing = _all_people()
    if matching.is_duplicate(avg_embedding, existing):
        raise HTTPException(
            status_code=409, detail="Duplicate enrollment: face already exists"
        )

    rows = db.query(
        """
        INSERT INTO people (name, age, embedding)
        VALUES (%s, %s, %s)
        RETURNING id, name, age, created_at
        """,
        (name.strip(), age, json.dumps(avg_embedding.tolist())),
        fetch=True,
    )
    person = PersonOut(**rows[0])
    return EnrollResponse(
        success=True, message=f"Enrolled {person.name} successfully", person=person
    )
