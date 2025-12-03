import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
import pandas as pd

@pytest.mark.asyncio
async def test_analyze_mocked(monkeypatch):
    async def fake_coords(city_name: str):
        return {"lat": 52.0, "lon": 21.0, "name": city_name}

    async def fake_current(lat: float, lon: float):
        return {"time": "2025-12-03T00:00:00Z", "temperature": 5.0, "humidity": 60.0, "wind_speed": 3.0}

    async def fake_hist(lat: float, lon: float):
        rows = []
        for i in range(24):
            rows.append({"timestamp": i + 1, "hour": i % 24, "humidity": 60.0, "wind_speed": 3.0, "temperature": 5.0 + (i % 5)})
        return pd.DataFrame(rows)

    from app import services
    monkeypatch.setattr(services.weather_service, "get_coordinates", fake_coords)
    monkeypatch.setattr(services.weather_service, "fetch_current_weather", fake_current)
    monkeypatch.setattr(services.weather_service, "fetch_historical_training_data", fake_hist)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/analyze", json={"city_name": "Warsaw"})
    assert resp.status_code == 200
    js = resp.json()
    assert js["city"] == "Warsaw"
    assert len(js["predictions"]) == 24
    assert "metrics" in js
