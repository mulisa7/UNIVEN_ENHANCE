from fastapi import APIRouter, HTTPException

import db
from schemas import PersonOut

router = APIRouter()


@router.get("/people", response_model=list[PersonOut])
async def list_people():
    return db.query(
        "SELECT id, name, age, created_at FROM people ORDER BY created_at DESC",
        fetch=True,
    )


@router.delete("/people/{person_id}")
async def delete_person(person_id: int):
    """POPIA erasure request: permanently removes a person's record, name,
    age, and embedding."""
    rows = db.query(
        "DELETE FROM people WHERE id = %s RETURNING id", (person_id,), fetch=True
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Person not found")
    return {"success": True, "deleted_id": person_id}
