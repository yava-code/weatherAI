import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlmodel import Session, select
from models import WeatherData
from datetime import timedelta, datetime
import numpy as np

def train_and_predict(session: Session):
    """
    Fetches the last 50 data points, trains a Linear Regression model,
    and predicts the temperature for the next 24 hours.
    """
    # Fetch last 50 records
    statement = select(WeatherData).order_by(WeatherData.timestamp.desc()).limit(50)
    results = session.exec(statement).all()
    
    if len(results) < 10:
        return None  # Not enough data

    # Convert to DataFrame
    data = [{"timestamp": r.timestamp, "temperature": r.temperature} for r in results]
    df = pd.DataFrame(data)
    
    # Sort by timestamp (ascending) for training
    df = df.sort_values("timestamp")
    
    # Feature Engineering: Convert timestamp to numeric (seconds since epoch)
    df["timestamp_num"] = df["timestamp"].apply(lambda x: x.timestamp())
    
    X = df[["timestamp_num"]]
    y = df["temperature"]
    
    # Train Model
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next 24 hours
    last_timestamp = df["timestamp"].iloc[-1]
    future_timestamps = [last_timestamp + timedelta(hours=i+1) for i in range(24)]
    future_timestamps_num = np.array([t.timestamp() for t in future_timestamps]).reshape(-1, 1)
    
    predictions = model.predict(future_timestamps_num)
    
    return {
        "timestamps": future_timestamps,
        "temperatures": predictions.tolist()
    }
