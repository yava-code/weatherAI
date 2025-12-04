import pytest
from app import worker
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_train_model_task(mocker):
    mock_train_model = mocker.patch('app.worker.train_model', new_callable=AsyncMock)
    worker.train_model_task.s().apply()
    mock_train_model.assert_called_once()

@pytest.mark.asyncio
async def test_run_global_monitor_error(mocker):
    mock_get_coordinates = mocker.patch('app.worker.get_coordinates', new_callable=AsyncMock, side_effect=Exception("API error"))
    await worker.run_global_monitor()
    assert mock_get_coordinates.call_count == 5

@pytest.mark.asyncio
async def test_run_global_monitor(mocker):
    mock_get_coordinates = mocker.patch('app.worker.get_coordinates', new_callable=AsyncMock)
    mock_fetch_current = mocker.patch('app.worker.fetch_current_weather', new_callable=AsyncMock)
    mocker.patch('app.worker.fetch_historical_training_data', new_callable=AsyncMock)
    mocker.patch('app.worker.load_model_for_city', return_value=(None, None))
    mocker.patch('app.worker.train_model_for_city')
    mocker.patch('app.worker.predict_temp', return_value=15.0)
    mock_redis_set = mocker.patch('app.worker.REDIS_CACHE.set')

    mock_get_coordinates.return_value = {"lat": 0, "lon": 0}
    mock_fetch_current.return_value = {"humidity": 60, "wind_speed": 10}

    await worker.run_global_monitor()

    assert mock_get_coordinates.call_count == 5
    assert mock_fetch_current.call_count == 5
    assert mock_redis_set.call_count == 5

@pytest.mark.asyncio
async def test_run_monitor_popular_cities(mocker):
    mock_get_coordinates = mocker.patch('app.worker.get_coordinates', new_callable=AsyncMock)
    mock_fetch_hist = mocker.patch('app.worker.fetch_historical_training_data', new_callable=AsyncMock)
    mock_train_model = mocker.patch('app.worker.train_model_for_city')

    mock_get_coordinates.side_effect = [
        {"lat": 0, "lon": 0},
        None,
        {"lat": 0, "lon": 0},
        {"lat": 0, "lon": 0},
        {"lat": 0, "lon": 0},
    ]

    await worker.run_monitor_popular_cities()

    assert mock_get_coordinates.call_count == 5
    assert mock_fetch_hist.call_count == 4
    assert mock_train_model.call_count == 4

@pytest.mark.asyncio
async def test_run_monitor_popular_cities_error(mocker):
    mock_get_coordinates = mocker.patch('app.worker.get_coordinates', new_callable=AsyncMock, side_effect=Exception("API error"))
    await worker.run_monitor_popular_cities()
    assert mock_get_coordinates.call_count == 5

@pytest.mark.asyncio
async def test_global_monitor_task(mocker):
    mock_run_global_monitor = mocker.patch('app.worker.run_global_monitor', new_callable=AsyncMock)
    worker.global_monitor_task.s().apply()
    mock_run_global_monitor.assert_called_once()

@pytest.mark.asyncio
async def test_monitor_popular_cities_task(mocker):
    mock_run_monitor_popular_cities = mocker.patch('app.worker.run_monitor_popular_cities', new_callable=AsyncMock)
    worker.monitor_popular_cities_task.s().apply()
    mock_run_monitor_popular_cities.assert_called_once()
