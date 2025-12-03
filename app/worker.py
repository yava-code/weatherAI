import os
import asyncio
from celery import Celery
from celery.schedules import crontab
from app.services.weather_service import fetch_weather_data
from app.services.ml_service import train_model

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("meteo_mind", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task
def fetch_weather_task():
    asyncio.run(fetch_weather_data())

@celery_app.task
def train_model_task():
    asyncio.run(train_model())

celery_app.conf.beat_schedule = {
    "fetch-weather-hourly": {
        "task": "app.worker.fetch_weather_task",
        "schedule": 60 * 60,
    },
    "train-model-daily": {
        "task": "app.worker.train_model_task",
        "schedule": crontab(hour=0, minute=0),
    },
}
