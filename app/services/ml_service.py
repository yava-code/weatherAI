import os
import time
import json
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal
from app.models.weather import WeatherMeasurement
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import joblib

MODELS_DIR = os.getenv("MODELS_DIR", "weather_models")
os.makedirs(MODELS_DIR, exist_ok=True)
CITY_MAP = {"Warsaw": 0, "Berlin": 1, "London": 2}

def _paths(city_slug: str):
    return (
        os.path.join(MODELS_DIR, f"{city_slug}.joblib"),
        os.path.join(MODELS_DIR, f"{city_slug}.metrics.json"),
    )

def _slug(name: str) -> str:
    return name.lower().replace(" ", "-")

async def train_model():
    async with AsyncSessionLocal() as session:  # type: AsyncSession
        result = await session.execute(select(WeatherMeasurement))
        rows = result.scalars().all()
    if not rows:
        return False
    df = pd.DataFrame([
        {
            "timestamp": int(time.mktime(r.timestamp.timetuple())),
            "hour": r.timestamp.hour,
            "humidity": r.humidity,
            "wind_speed": r.wind_speed,
            "temperature": r.temperature,
            "city_code": CITY_MAP.get(r.city, -1),
        }
        for r in rows
        if r.temperature is not None and r.city in CITY_MAP
    ])
    if len(df) < 10:
        return False
    X = df[["timestamp", "hour", "humidity", "wind_speed", "city_code"]]
    y = df["temperature"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    metrics = {
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "last_trained": time.strftime("%Y-%m-%d %H:%M:%S"),
        "feature_importance": dict(zip(X.columns, model.feature_importances_)),
    }
    model_path, metrics_path = _paths("global")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f)
    joblib.dump(model, model_path)
    return True

def predict_temp(timestamp: float, humidity: float, wind_speed: float, city: str) -> float:
    slug = _slug(city)
    model_path, _ = _paths(slug)
    if not os.path.exists(model_path):
        raise FileNotFoundError("Model not trained")
    model = joblib.load(model_path)
    city_code = CITY_MAP.get(city, 0)
    dt_struct = time.localtime(timestamp)
    hour = dt_struct.tm_hour
    X = pd.DataFrame([[timestamp, hour, humidity, wind_speed, city_code]], columns=["timestamp", "hour", "humidity", "wind_speed", "city_code"])
    pred = model.predict(X)[0]
    return float(pred)

def train_model_for_city(city_name: str, df: pd.DataFrame):
    if df is None or df.empty:
        return False
    if len(df) < 10:
        return False
    X = df[["timestamp", "hour", "humidity", "wind_speed"]]
    y = df["temperature"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    metrics = {
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "last_trained": time.strftime("%Y-%m-%d %H:%M:%S"),
        "feature_importance": dict(zip(X.columns, model.feature_importances_)),
    }
    slug = _slug(city_name)
    model_path, metrics_path = _paths(slug)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f)
    joblib.dump(model, model_path)
    return True

def load_model_for_city(city_name: str):
    slug = _slug(city_name)
    model_path, metrics_path = _paths(slug)
    if not os.path.exists(model_path):
        return None, None
    model = joblib.load(model_path)
    metrics = None
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
    return model, metrics
