import os
import time
import pandas as pd
import psycopg2
import streamlit as st
import altair as alt
import joblib

st.set_page_config(page_title="MeteoMind Dashboard", layout="wide")

dsn = os.getenv("DATABASE_URL", "postgresql://meteo:meteo_pass@db/meteo_mind")
conn = psycopg2.connect(dsn)
df = pd.read_sql(
    "SELECT city, timestamp, temperature, humidity, wind_speed FROM weather_measurements ORDER BY timestamp DESC",
    conn,
)

top = st.columns(3)
total_records = len(df)
avg_temp = float(df["temperature"].mean()) if not df.empty else 0.0
last_update = str(df["timestamp"].max()) if not df.empty else "n/a"
top[0].metric("Total Records", total_records)
top[1].metric("Avg Temp", f"{avg_temp:.2f} °C")
top[2].metric("Last Update", last_update)

st.subheader("Temperature Trends")
df_chart = df.copy()
df_chart["timestamp"] = pd.to_datetime(df_chart["timestamp"])
area = (
    alt.Chart(df_chart)
    .mark_area(opacity=0.6)
    .encode(
        x=alt.X("timestamp:T", title="Time"),
        y=alt.Y("temperature:Q", title="Temperature (°C)"),
        color=alt.Color("city:N", legend=alt.Legend(title="City")),
        tooltip=["city", "timestamp", "temperature", "humidity", "wind_speed"],
    )
    .properties(height=320)
)
st.altair_chart(area, use_container_width=True)

st.subheader("AI Forecaster")
col1, col2 = st.columns(2)
humidity = col1.slider("Humidity (%)", min_value=0, max_value=100, value=50)
wind = col2.slider("Wind Speed (m/s)", min_value=0.0, max_value=30.0, value=5.0)

model_path = os.getenv("MODEL_PATH", "weather_model.joblib")
now_ts = int(time.time())
predict_btn = st.button("Predict")
if predict_btn:
    try:
        model = joblib.load(model_path)
        X = pd.DataFrame([[now_ts, humidity, wind]], columns=["timestamp", "humidity", "wind_speed"])
        y_pred = float(model.predict(X)[0])
        st.success(f"Predicted Temperature: {y_pred:.2f} °C")
    except FileNotFoundError:
        st.warning("Model not trained yet. Come back after nightly training.")
    except Exception as e:
        st.error(str(e))
