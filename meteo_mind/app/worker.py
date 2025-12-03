from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
from app.services.weather_service import fetch_weather_data
from app.services.ml_service import train_model
import asyncio

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.beat_schedule = {
    "fetch-weather-every-hour": {
        "task": "app.worker.fetch_weather_task",
        "schedule": crontab(minute=0, hour="*"),  # Every hour
    },
    "train-model-daily": {
        "task": "app.worker.train_model_task",
        "schedule": crontab(minute=0, hour=0),  # Daily at midnight
    },
}

@celery_app.task
def fetch_weather_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_weather_data())
    return "Weather data fetched"

@celery_app.task
def train_model_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(train_model())
    return "Model trained"
