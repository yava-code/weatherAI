import os
import asyncio
from celery import Celery
from celery.schedules import crontab
from app.services.ml_service import train_model
from app.services.weather_service import get_coordinates, fetch_current_weather, fetch_historical_training_data
from app.services.ml_service import train_model_for_city, load_model_for_city, predict_temp
import time
import json
import redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("meteo_mind", broker=REDIS_URL, backend=REDIS_URL)
REDIS_CACHE = redis.Redis.from_url(REDIS_URL)

@celery_app.task
def train_model_task():
    """Celery task to train the global machine learning model."""
    asyncio.run(train_model())

@celery_app.task
def global_monitor_task():
    """
    Celery task that monitors a list of global cities.

    For each city, it fetches weather data, makes predictions, and caches
    the results in Redis.
    """
    cities = ["London", "New York", "Tokyo", "Warsaw", "Berlin"]
    for city in cities:
        try:
            coords = asyncio.run(get_coordinates(city))
            if not coords:
                continue
            current = asyncio.run(fetch_current_weather(coords["lat"], coords["lon"]))
            if not current:
                continue
            hist_df = asyncio.run(fetch_historical_training_data(coords["lat"], coords["lon"]))
            model, metrics = load_model_for_city(city)
            if model is None:
                train_model_for_city(city, hist_df)
                model, metrics = load_model_for_city(city)
            preds = []
            now = int(time.time())
            humidity = float(current.get("humidity") or 50)
            wind = float(current.get("wind_speed") or 5)
            for h in range(1, 25):
                ts = now + h * 3600
                y = predict_temp(ts, humidity, wind, city)
                preds.append({"timestamp": ts, "hour": h, "temperature": y})
            payload = {"city": city, "coords": coords, "current": current, "predictions": preds, "metrics": metrics or {}}
            REDIS_CACHE.set(f"city_intel:{city}", json.dumps(payload), ex=3600)
        except Exception:
            continue

@celery_app.task
def monitor_popular_cities_task():
    """
    Celery task that trains models for a list of popular cities.

    This ensures that models for these cities are regularly updated with
    the latest historical data.
    """
    cities = ["London", "Warsaw", "Berlin", "Paris", "New York"]
    for city in cities:
        try:
            coords = asyncio.run(get_coordinates(city))
            if not coords:
                continue
            hist_df = asyncio.run(fetch_historical_training_data(coords["lat"], coords["lon"]))
            train_model_for_city(city, hist_df)
        except Exception:
            continue

celery_app.conf.beat_schedule = {
    "train-model-daily": {
        "task": "app.worker.train_model_task",
        "schedule": crontab(hour=0, minute=0),
    },
    "global-monitor-hourly": {
        "task": "app.worker.global_monitor_task",
        "schedule": 60 * 60,
    },
    "monitor-popular-cities": {
        "task": "app.worker.monitor_popular_cities_task",
        "schedule": 30 * 60,
    },
}
