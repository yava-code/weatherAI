from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime

class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""
    pass

class WeatherMeasurement(Base):
    """
    Represents a weather measurement record in the database.

    Attributes:
        id (int): The primary key.
        city (str): The name of the city for the measurement.
        timestamp (datetime): The timestamp of the measurement.
        temperature (float): The temperature in degrees Celsius.
        humidity (float): The humidity as a percentage.
        wind_speed (float): The wind speed in km/h.
    """
    __tablename__ = "weather_measurements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    temperature: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float] = mapped_column(Float)
    wind_speed: Mapped[float] = mapped_column(Float)
