from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import Session, select, func
from database import create_db_and_tables, get_session
from models import WeatherData, WeatherDataCreate, WeatherDataRead, PredictionResponse, StatsResponse
from ml_engine import train_and_predict
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (for index.html)
# We will mount it later or just serve index.html at root if it exists
# For now, let's just serve the index.html at root

@app.get("/")
async def read_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "Welcome to Weather Prediction API. index.html not found."}

@app.post("/ingest", response_model=WeatherDataRead)
def ingest_data(data: WeatherDataCreate, session: Session = Depends(get_session)):
    weather_data = WeatherData.from_orm(data)
    session.add(weather_data)
    session.commit()
    session.refresh(weather_data)
    return weather_data

@app.get("/stats", response_model=StatsResponse)
def get_stats(session: Session = Depends(get_session)):
    count = session.exec(select(func.count(WeatherData.id))).one()
    avg_temp = session.exec(select(func.avg(WeatherData.temperature))).one()
    
    if avg_temp is None:
        avg_temp = 0.0
        
    return StatsResponse(count=count, average_temperature=avg_temp)

@app.get("/predict", response_model=PredictionResponse)
def get_prediction(session: Session = Depends(get_session)):
    prediction = train_and_predict(session)
    if not prediction:
        raise HTTPException(status_code=400, detail="Not enough data to make a prediction (need at least 10 records).")
    return PredictionResponse(**prediction)
