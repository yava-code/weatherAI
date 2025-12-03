import os
import pandas as pd
from app.services.ml_service import train_model_for_city, load_model_for_city, predict_temp

def test_train_and_predict_city_model(tmp_path, monkeypatch):
    monkeypatch.setenv("MODELS_DIR", str(tmp_path))
    df = pd.DataFrame({
        "timestamp": [1,2,3,4,5,6,7,8,9,10,11,12],
        "hour": [0,1,2,3,4,5,6,7,8,9,10,11],
        "humidity": [50]*12,
        "wind_speed": [5]*12,
        "temperature": [10,11,12,13,14,15,16,17,18,19,20,21],
    })
    ok = train_model_for_city("TestCity", df)
    assert ok
    y = predict_temp(1, 50, 5, "TestCity")
    assert y is not None

def test_train_and_load_city_model(tmp_path, monkeypatch):
    monkeypatch.setenv("MODELS_DIR", str(tmp_path))
    df = pd.DataFrame({
        "timestamp": [1,2,3,4,5,6,7,8,9,10,11,12],
        "hour": [0,1,2,3,4,5,6,7,8,9,10,11],
        "humidity": [50]*12,
        "wind_speed": [5]*12,
        "temperature": [10,11,12,13,14,15,16,17,18,19,20,21],
    })
    ok = train_model_for_city("TestCity", df)
    assert ok
    model, metrics = load_model_for_city("TestCity")
    assert model is not None
    assert metrics is not None
