import os
import asyncio
from celery import Celery
from app.services.weather_service import fetch_weather_data

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("meteo_mind", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task
def fetch_weather_task():
    asyncio.run(fetch_weather_data())
