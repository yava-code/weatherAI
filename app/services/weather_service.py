import logging
from datetime import datetime
import time
import asyncio
import httpx
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def _get_json(url: str, params: dict, retries: int = 3):
    """
    Asynchronously fetches JSON data from a URL with retries.

    Args:
        url (str): The URL to fetch data from.
        params (dict): A dictionary of query parameters.
        retries (int): The number of times to retry the request.

    Returns:
        dict: The JSON response as a dictionary, or None if the request fails.
    """
    timeout = httpx.Timeout(10.0, connect=5.0, read=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for i in range(retries):
            try:
                r = await client.get(url, params=params)
                r.raise_for_status()
                return r.json()
            except httpx.TimeoutException:
                if i < retries - 1:
                    await asyncio.sleep(0.5 * (i + 1))
                else:
                    return None
            except Exception:
                return None

async def get_coordinates(city_name: str):
    """
    Fetches the geographical coordinates (latitude and longitude) for a city.

    Args:
        city_name (str): The name of the city.

    Returns:
        dict: A dictionary containing the latitude, longitude, and name of the city,
              or None if the city is not found.
    """
    js = await _get_json(
        "https://geocoding-api.open-meteo.com/v1/search",
        {"name": city_name, "count": 1, "language": "en"},
    )
    if not js:
        return None
    results = js.get("results") or []
    if not results:
        return None
    item = results[0]
    return {"lat": item["latitude"], "lon": item["longitude"], "name": item.get("name", city_name)}

async def fetch_current_weather(lat: float, lon: float):
    """
    Fetches the current weather for a given latitude and longitude.

    Args:
        lat (float): The latitude.
        lon (float): The longitude.

    Returns:
        dict: A dictionary containing the current weather data (time, temperature,
              humidity, and wind speed), or None if the request fails.
    """
    js = await _get_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            "timezone": "UTC",
        },
    )
    if not js:
        return None
    cur = js.get("current", {})
    return {
        "time": cur.get("time"),
        "temperature": cur.get("temperature_2m"),
        "humidity": cur.get("relative_humidity_2m"),
        "wind_speed": cur.get("wind_speed_10m"),
    }

async def fetch_historical_training_data(lat: float, lon: float):
    """
    Fetches historical weather data for the past 30 days for training purposes.

    Args:
        lat (float): The latitude.
        lon (float): The longitude.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the historical weather data,
                      or an empty DataFrame if the request fails.
    """
    js = await _get_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            "past_days": 30,
            "timezone": "UTC",
        },
    )
    if not js:
        return pd.DataFrame()
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
