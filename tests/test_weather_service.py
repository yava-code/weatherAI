import pytest
from app.services import weather_service
import httpx

@pytest.mark.asyncio
async def test_get_json_timeout(mocker):
    mocker.patch('httpx.AsyncClient.get', side_effect=httpx.TimeoutException("timeout"))
    result = await weather_service._get_json("http://test.com", {})
    assert result is None

@pytest.mark.asyncio
async def test_get_json_error(mocker):
    mocker.patch('httpx.AsyncClient.get', side_effect=Exception("error"))
    result = await weather_service._get_json("http://test.com", {})
    assert result is None

@pytest.mark.asyncio
async def test_get_coordinates_no_results(mocker):
    mocker.patch('app.services.weather_service._get_json', return_value={"results": []})
    result = await weather_service.get_coordinates("test")
    assert result is None

@pytest.mark.asyncio
async def test_get_coordinates_no_js(mocker):
    mocker.patch('app.services.weather_service._get_json', return_value=None)
    result = await weather_service.get_coordinates("test")
    assert result is None

@pytest.mark.asyncio
async def test_fetch_current_weather_no_js(mocker):
    mocker.patch('app.services.weather_service._get_json', return_value=None)
    result = await weather_service.fetch_current_weather(0, 0)
    assert result is None

@pytest.mark.asyncio
async def test_fetch_historical_training_data_no_js(mocker):
    mocker.patch('app.services.weather_service._get_json', return_value=None)
    result = await weather_service.fetch_historical_training_data(0, 0)
    assert result.empty is True
