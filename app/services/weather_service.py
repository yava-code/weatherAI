import logging
from datetime import datetime
import time
import httpx
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_coordinates(city_name: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city_name, "count": 1, "language": "en"},
        )
        r.raise_for_status()
        js = r.json()
        results = js.get("results") or []
        if not results:
            return None
        item = results[0]
        return {"lat": item["latitude"], "lon": item["longitude"], "name": item.get("name", city_name)}

async def fetch_current_weather(lat: float, lon: float):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
                "timezone": "UTC",
            },
        )
        r.raise_for_status()
        js = r.json()
        cur = js.get("current", {})
        return {
            "time": cur.get("time"),
            "temperature": cur.get("temperature_2m"),
            "humidity": cur.get("relative_humidity_2m"),
            "wind_speed": cur.get("wind_speed_10m"),
        }

async def fetch_historical_training_data(lat: float, lon: float):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
                "past_days": 30,
                "timezone": "UTC",
            },
        )
        r.raise_for_status()
        js = r.json()
        hourly = js.get("hourly", {})
        times = hourly.get("time") or []
        temps = hourly.get("temperature_2m") or []
        hums = hourly.get("relative_humidity_2m") or []
        winds = hourly.get("wind_speed_10m") or []
        rows = []
        for t, temp, h, w in zip(times, temps, hums, winds):
            dt = datetime.fromisoformat(t)
            rows.append(
                {
                    "timestamp": int(time.mktime(dt.timetuple())),
                    "hour": dt.hour,
                    "humidity": h,
                    "wind_speed": w,
                    "temperature": temp,
                }
            )
        return pd.DataFrame(rows)
