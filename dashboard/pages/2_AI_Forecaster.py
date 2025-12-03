import streamlit as st
import pandas as pd
import joblib
import os
import time

st.set_page_config(page_title="AI Forecast", page_icon="🔮", layout="wide")

st.title("🔮 AI Temperature Forecaster")
st.markdown("Uses RandomForestRegressor trained on historical data to predict temperature based on conditions.")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Input Parameters")
    city = st.selectbox("Select Target City", ["Warsaw", "Berlin", "London"])
    humidity = st.slider("Target Humidity (%)", 0, 100, 50)
    wind_kmh = st.slider("Wind Speed (km/h)", 0.0, 40.0, 10.0)
    predict_btn = st.button("Generate Forecast", type="primary")

with col2:
    st.markdown("### Prediction Result")
    model_path = os.getenv("MODEL_PATH", "weather_model.joblib")
    if predict_btn:
        CITY_MAP = {"Warsaw": 0, "Berlin": 1, "London": 2}
        try:
            model = joblib.load(model_path)
            now_ts = int(time.time())
            future_ts = now_ts + 3600
            city_code = CITY_MAP.get(city, 0)
            wind_ms = float(wind_kmh) / 3.6
            X = pd.DataFrame(
                [[future_ts, humidity, wind_ms, city_code]],
                columns=["timestamp", "humidity", "wind_speed", "city_code"],
            )
            prediction = model.predict(X)[0]
            st.metric(label=f"Predicted Temp for {city}", value=f"{prediction:.2f} °C")
            if prediction < 10:
                st.info("It will be cold. Wear a jacket.")
            elif prediction > 25:
                st.success("Great weather expected!")
            else:
                st.info("Moderate weather conditions.")
        except FileNotFoundError:
            st.error("Model not trained yet. The system trains daily at midnight.")
        except Exception as e:
            st.error(f"Prediction Engine Error: {e}")
