from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.db import Base
from datetime import datetime

class WeatherMeasurement(Base):
    __tablename__ = "weather_measurements"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    city = Column(String, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
