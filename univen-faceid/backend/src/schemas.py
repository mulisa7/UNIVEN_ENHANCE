"""Team 4 — response/request models.

Response models intentionally have no `embedding` field, so raw embeddings
can never leak into a public-facing API response even by accident.
"""

from datetime import datetime

from pydantic import BaseModel


class PersonOut(BaseModel):
    id: int
    name: str
    age: int
    created_at: datetime


class EnrollResponse(BaseModel):
    success: bool
    message: str
    person: PersonOut


class RecognizeResponse(BaseModel):
    matched: bool
    person: PersonOut | None = None
    confidence: float
