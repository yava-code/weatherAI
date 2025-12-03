import logging
from datetime import datetime
import httpx
from app.core.db import AsyncSessionLocal
from app.models.weather import WeatherMeasurement

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CITIES = {
    "Warsaw": {"lat": 52.2297, "lon": 21.0122},
    "Berlin": {"lat": 52.5200, "lon": 13.4050},
    "London": {"lat": 51.5074, "lon": -0.1278},
}

async def fetch_weather_data():
    async with httpx.AsyncClient() as client:
        for city_name, coords in CITIES.items():
            try:
                response = await client.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": coords["lat"],
                        "longitude": coords["lon"],
                        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
                    },
                )
                response.raise_for_status()
                data = response.json()
                current = data.get("current", {})

                measurement = WeatherMeasurement(
                    city=city_name,
                    timestamp=datetime.fromisoformat(current.get("time")),
                    temperature=current.get("temperature_2m"),
                    humidity=current.get("relative_humidity_2m"),
                    wind_speed=current.get("wind_speed_10m"),
                )

                async with AsyncSessionLocal() as session:
                    session.add(measurement)
                    await session.commit()

                logger.info(f"Successfully fetched data for {city_name}")
            except Exception as e:
                logger.error(f"Error fetching data for {city_name}: {e}")
