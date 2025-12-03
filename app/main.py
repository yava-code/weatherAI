from fastapi import FastAPI
from app.core.db import init_db

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
def root():
    return {"message": "MeteoMind API"}

@app.get("/health")
def health():
    return {"status": "ok"}
