from fastapi import FastAPI, HTTPException
from app.core.db import init_db
from app.worker import train_model_task
import os
import json
import time
import httpx
from app.services.weather_service import get_coordinates, fetch_current_weather, fetch_historical_training_data
from app.services.ml_service import train_model_for_city, load_model_for_city, predict_temp

app = FastAPI(
    title="MeteoMind API",
    description="A FastAPI application for weather prediction using machine learning.",
    version="1.0.0",
)

@app.on_event("startup")
async def on_startup():
    """Initializes the database connection on application startup."""
    await init_db()

@app.get("/")
def root():
    """Returns a welcome message for the MeteoMind API."""
    return {"message": "MeteoMind API"}

@app.get("/health")
def health():
    """Returns the health status of the application."""
    return {"status": "ok"}

@app.post("/trigger-train")
def trigger_train():
    """
    Triggers a background task to train the global machine learning model.

    Returns:
        dict: A status message indicating that the training has been scheduled.

    Raises:
        HTTPException: If the training task could not be scheduled.
    """
    try:
        train_model_task.delay()
        return {"status": "scheduled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def get_metrics():
    """
    Retrieves the metrics of the globally trained machine learning model.

    Returns:
        dict: A dictionary containing the model's metrics.

    Raises:
        HTTPException: If the metrics file is not found.
    """
    path = os.path.join("weather_models", "global.metrics.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="metrics not found")

@app.post("/analyze")
async def analyze(payload: dict):
    """
    Analyzes weather data for a specific city, returning current weather,
    temperature predictions, and model metrics.

    If no model exists for the city, a new one will be trained.

    Args:
        payload (dict): A dictionary containing the city name.
            Example: {"city_name": "London"}

    Returns:
        dict: A dictionary containing the city's coordinates, current weather,
              temperature predictions for the next 24 hours, and model metrics.

    Raises:
        HTTPException: If the city name is not provided, if the city is not found,
                       if weather data cannot be fetched, or if the model training fails.
    """
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
