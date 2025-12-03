from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class WeatherData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime
    temperature: float
    humidity: float
    pressure: float

class WeatherDataCreate(SQLModel):
    timestamp: datetime
    temperature: float
    humidity: float
    pressure: float

class WeatherDataRead(WeatherDataCreate):
    id: int

class PredictionResponse(SQLModel):
    timestamps: list[datetime]
    temperatures: list[float]

class StatsResponse(SQLModel):
    count: int
    average_temperature: float
