import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy import select
from app.core.db import AsyncSessionLocal
from app.models.weather import WeatherMeasurement
import os

MODEL_PATH = "weather_model.joblib"

async def train_model():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(WeatherMeasurement))
        measurements = result.scalars().all()

    if not measurements:
        print("No data to train on.")
        return

    df = pd.DataFrame([
        {
            "timestamp": m.timestamp.timestamp(),
            "humidity": m.humidity,
            "wind_speed": m.wind_speed,
            "temperature": m.temperature
        } for m in measurements
    ])

    X = df[["timestamp", "humidity", "wind_speed"]]
    y = df["temperature"]

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    print("Model trained and saved.")

def predict_weather(timestamp: float, humidity: float, wind_speed: float):
    if not os.path.exists(MODEL_PATH):
        return None
    
    model = joblib.load(MODEL_PATH)
    prediction = model.predict([[timestamp, humidity, wind_speed]])
    return prediction[0]
