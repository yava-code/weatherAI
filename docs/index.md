# MeteoMind: Weather Intelligence Platform

Welcome to the MeteoMind documentation.

MeteoMind is an end‑to‑end system for collecting, analyzing and forecasting weather data, built with a service‑oriented architecture.

## Architecture

- Backend: FastAPI (Python 3.11)
- Frontend: Streamlit
- ML Engine: scikit‑learn (RandomForest)
- Database: PostgreSQL
- Async Tasks: Celery + Redis
- Infrastructure: Docker Compose

## Installation

```bash
git clone https://github.com/your-username/meteo-mind.git
cd meteo-mind
docker-compose up --build
```
