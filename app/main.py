from fastapi import FastAPI, HTTPException
from app.core.db import init_db
from app.worker import train_model_task
import os
import json

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

@app.post("/trigger-train")
def trigger_train():
    try:
        train_model_task.delay()
        return {"status": "scheduled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def get_metrics():
    path = "model_metrics.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="metrics not found")
    with open(path, "r") as f:
        return json.load(f)
