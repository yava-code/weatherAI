import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
import os

@pytest.mark.asyncio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "MeteoMind API"

@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_trigger_train(mocker):
    mocker.patch('app.main.train_model_task.delay', return_value=None)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/trigger-train")
    assert resp.status_code == 200
    assert resp.json()["status"] == "scheduled"

@pytest.mark.asyncio
async def test_trigger_train_error(mocker):
    mocker.patch('app.main.train_model_task.delay', side_effect=Exception("error"))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/trigger-train")
    assert resp.status_code == 500

@pytest.mark.asyncio
async def test_get_metrics(mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data='{"mae": 0.5}'))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/metrics")
    assert resp.status_code == 200
    assert resp.json()["mae"] == 0.5

@pytest.mark.asyncio
async def test_get_metrics_not_found(mocker):
    mocker.patch('os.path.exists', return_value=False)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/metrics")
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_analyze_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/analyze", json={})
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_analyze_geocoding_timeout(mocker):
    mocker.patch('app.main.get_coordinates', return_value=None)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/analyze", json={"city_name": "test"})
    assert resp.status_code == 504

@pytest.mark.asyncio
async def test_analyze_weather_fetch_timeout(mocker):
    mocker.patch('app.main.get_coordinates', return_value={"lat": 0, "lon": 0})
    mocker.patch('app.main.fetch_current_weather', return_value=None)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/analyze", json={"city_name": "test"})
    assert resp.status_code == 504

@pytest.mark.asyncio
async def test_analyze_training_failed(mocker):
    mocker.patch('app.main.get_coordinates', return_value={"lat": 0, "lon": 0})
    mocker.patch('app.main.fetch_current_weather', return_value={"humidity": 50, "wind_speed": 5})
    mocker.patch('app.main.fetch_historical_training_data', return_value=None)
    mocker.patch('app.main.load_model_for_city', return_value=(None, None))
    mocker.patch('app.main.train_model_for_city', return_value=False)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/analyze", json={"city_name": "test"})
    assert resp.status_code == 500
