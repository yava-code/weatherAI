from fastapi import FastAPI, HTTPException
from app.core.db import init_db
from app.worker import train_model_task
import os
import json
import time
import httpx
from app.services.weather_service import get_coordinates, fetch_current_weather, fetch_historical_training_data
from app.services.ml_service import train_model_for_city, load_model_for_city, predict_temp

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
    path = os.path.join("weather_models", "global.metrics.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="metrics not found")

@app.post("/analyze")
async def analyze(payload: dict):
    city_name = (payload or {}).get("city_name")
    if not city_name:
        raise HTTPException(status_code=422, detail="city_name required")
    coords = await get_coordinates(city_name)
    if not coords:
        raise HTTPException(status_code=504, detail="geocoding timeout or city not found")
    current = await fetch_current_weather(coords["lat"], coords["lon"])
    if not current:
        raise HTTPException(status_code=504, detail="current weather fetch timeout")
    hist_df = await fetch_historical_training_data(coords["lat"], coords["lon"])
    model, metrics = load_model_for_city(city_name)
    if model is None:
        ok = train_model_for_city(city_name, hist_df)
        if not ok:
            raise HTTPException(status_code=500, detail="training failed")
        model, metrics = load_model_for_city(city_name)
    preds = []
    now = int(time.time())
    humidity = float(current.get("humidity") or 50)
    wind = float(current.get("wind_speed") or 5)
    for h in range(1, 25):
        ts = now + h * 3600
        y = predict_temp(ts, humidity, wind, city_name)
        preds.append({"timestamp": ts, "hour": h, "temperature": y})
    return {
        "city": city_name,
        "coords": coords,
        "current": current,
        "predictions": preds,
        "metrics": metrics or {},
    }
