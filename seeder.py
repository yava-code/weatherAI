import random
from datetime import datetime, timedelta
from sqlmodel import Session
from database import engine, create_db_and_tables
from models import WeatherData

def seed_data():
    create_db_and_tables()
    with Session(engine) as session:
        # Check if data already exists
        if session.query(WeatherData).count() > 0:
            print("Database already contains data. Skipping seed.")
            return

        print("Seeding database...")
        base_time = datetime.now() - timedelta(days=7)
        
        # Generate hourly data for the last 7 days
        for i in range(7 * 24):
            current_time = base_time + timedelta(hours=i)
            
            # Simulate a daily temperature cycle
            # Base temp 20, varies by +/- 5 degrees based on hour of day
            hour_factor = -5 * (1 - abs((current_time.hour - 14) / 12)) 
            # Add some randomness
            temp = 20 + hour_factor + random.uniform(-2, 2)
            
            humidity = random.uniform(30, 80)
            pressure = random.uniform(1000, 1020)
            
            weather_data = WeatherData(
                timestamp=current_time,
                temperature=round(temp, 2),
                humidity=round(humidity, 2),
                pressure=round(pressure, 2)
            )
            session.add(weather_data)
        
        session.commit()
        print("Seeding complete!")

if __name__ == "__main__":
    seed_data()
