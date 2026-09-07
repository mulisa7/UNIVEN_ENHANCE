from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import enroll, people, recognize

app = FastAPI(title="Univen FaceID")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(enroll.router)
app.include_router(recognize.router)
app.include_router(people.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
