from fastapi import FastAPI
from app.core.db import engine, Base
from app.worker import fetch_weather_task, train_model_task

app = FastAPI(title="MeteoMind API")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def read_root():
    return {"message": "Welcome to MeteoMind API"}

@app.post("/trigger-fetch")
def trigger_fetch():
    fetch_weather_task.delay()
    return {"message": "Weather fetch task triggered"}

@app.post("/trigger-train")
def trigger_train():
    train_model_task.delay()
    return {"message": "Model training task triggered"}
