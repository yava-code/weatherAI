import streamlit as st
import pandas as pd
import joblib
import os
import time
import json
import altair as alt

st.set_page_config(page_title="AI Forecast", page_icon="🔮", layout="wide")

st.title("🔮 AI Temperature Forecaster")
st.markdown("Predictive engine using RandomForestRegressor with enhanced feature engineering and XAI insights.")

METRICS_PATH = "model_metrics.json"
metrics = None
if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH, "r") as f:
        metrics = json.load(f)
    m1, m2, m3 = st.columns(3)
    m1.metric("Model Accuracy (R²)", f"{metrics['r2']*100:.1f}%")
    m2.metric("Mean Error (MAE)", f"±{metrics['mae']:.2f}°C")
    m3.metric("Last Trained", metrics["last_trained"]) 
    st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🎛️ Simulation Parameters")
    city = st.selectbox("Target City", ["Warsaw", "Berlin", "London"])
    humidity = st.slider("Humidity (%)", 0, 100, 50)
    wind_kmh = st.slider("Wind Speed (km/h)", 0.0, 40.0, 10.0)
    hour_offset = st.slider("Forecast Horizon (Hours)", 1, 24, 1)
    predict_btn = st.button("Generate Forecast", type="primary")

with col2:
    st.markdown("### Prediction Result")
    model_path = os.getenv("MODEL_PATH", "weather_model.joblib")
    if predict_btn:
        CITY_MAP = {"Warsaw": 0, "Berlin": 1, "London": 2}
        try:
            model = joblib.load(model_path)
            now_ts = int(time.time())
            future_ts = now_ts + (hour_offset * 3600)
            future_struct = time.localtime(future_ts)
            future_hour = future_struct.tm_hour
            city_code = CITY_MAP.get(city, 0)
            wind_ms = float(wind_kmh) / 3.6
            X = pd.DataFrame(
                [[future_ts, future_hour, humidity, wind_ms, city_code]],
                columns=["timestamp", "hour", "humidity", "wind_speed", "city_code"],
            )
            prediction = model.predict(X)[0]
            st.metric(label=f"Forecast for {city} (+{hour_offset}h)", value=f"{prediction:.2f} °C")
            if metrics and "feature_importance" in metrics:
                st.markdown("#### Why this prediction?")
                fi_data = pd.DataFrame({
                    "Feature": list(metrics["feature_importance"].keys()),
                    "Importance": list(metrics["feature_importance"].values()),
                }).sort_values(by="Importance", ascending=False)
                chart = alt.Chart(fi_data).mark_bar().encode(
                    x=alt.X("Importance", axis=None),
                    y=alt.Y("Feature", sort="-x"),
                    color=alt.Color("Importance", scale=alt.Scale(scheme="greens")),
                    tooltip=["Feature", "Importance"],
                ).properties(height=200)
                st.altair_chart(chart, use_container_width=True)
                st.caption("Shows which factors most influenced the model's decision.")
        except FileNotFoundError:
            st.error("Model not trained yet. Trigger training or wait for scheduler.")
        except Exception as e:
            st.error(f"Error: {e}")
