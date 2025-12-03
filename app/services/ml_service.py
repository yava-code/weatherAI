import os
import time
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal
from app.models.weather import WeatherMeasurement
from sklearn.ensemble import RandomForestRegressor
import joblib

MODEL_PATH = os.getenv("MODEL_PATH", "weather_model.joblib")

async def train_model():
    async with AsyncSessionLocal() as session:  # type: AsyncSession
        result = await session.execute(select(WeatherMeasurement))
        rows = result.scalars().all()
    if not rows:
        return False
    df = pd.DataFrame([
        {
            "timestamp": int(time.mktime(r.timestamp.timetuple())),
            "humidity": r.humidity,
            "wind_speed": r.wind_speed,
            "temperature": r.temperature,
            "city": r.city,
        }
        for r in rows
        if r.temperature is not None and r.humidity is not None and r.wind_speed is not None
    ])
    if df.empty:
        return False
    X = df[["timestamp", "humidity", "wind_speed"]]
    y = df["temperature"]
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    return True

def predict_temp(timestamp: float, humidity: float, wind_speed: float) -> float:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not trained")
    model = joblib.load(MODEL_PATH)
    X = pd.DataFrame([[timestamp, humidity, wind_speed]], columns=["timestamp", "humidity", "wind_speed"])
    pred = model.predict(X)[0]
    return float(pred)
