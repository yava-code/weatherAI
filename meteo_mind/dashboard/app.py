import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import altair as alt
from app.services.ml_service import predict_weather
import joblib

# Page Config
st.set_page_config(page_title="MeteoMind Dashboard", layout="wide")

st.title("MeteoMind: Intelligent Weather Analytics")

# Database Connection
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    st.error("DATABASE_URL environment variable not set.")
    st.stop()

@st.cache_resource
def get_engine():
    return create_engine(DB_URL)

engine = get_engine()

# Fetch Data
st.header("Historical Weather Data")

try:
    query = "SELECT * FROM weather_measurements ORDER BY timestamp DESC"
    df = pd.read_sql(query, engine)
    
    if not df.empty:
        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Measurements", len(df))
        col2.metric("Cities Tracked", df['city'].nunique())
        col3.metric("Avg Temperature", f"{df['temperature'].mean():.2f} °C")

        # Charts
        st.subheader("Temperature Trends")
        chart = alt.Chart(df).mark_line().encode(
            x='timestamp:T',
            y='temperature:Q',
            color='city:N',
            tooltip=['timestamp', 'city', 'temperature', 'humidity']
        ).interactive()
        st.altair_chart(chart, use_container_width=True)

        st.subheader("Raw Data")
        st.dataframe(df)
    else:
        st.info("No data available yet. Trigger the fetch task!")

except Exception as e:
    st.error(f"Error connecting to database: {e}")

# Prediction Section
st.divider()
st.header("Real-time Prediction Model")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Predict Temperature")
    humidity = st.slider("Humidity (%)", 0, 100, 50)
    wind_speed = st.slider("Wind Speed (km/h)", 0.0, 50.0, 10.0)
    timestamp = pd.Timestamp.now().timestamp()
    
    if st.button("Predict"):
        try:
            # We need to load the model. 
            # Since dashboard is in a separate container, it needs access to the model file.
            # In docker-compose, we mounted .:/app, so they share the volume.
            # However, we need to make sure the model path is correct.
            model_path = "weather_model.joblib"
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                prediction = model.predict([[timestamp, humidity, wind_speed]])[0]
                st.success(f"Predicted Temperature: {prediction:.2f} °C")
            else:
                st.warning("Model not trained yet. Please trigger model training.")
        except Exception as e:
            st.error(f"Prediction error: {e}")

with col2:
    st.subheader("Control Panel")
    if st.button("Trigger Data Fetch"):
        # We can't easily call celery task from here without importing app.worker
        # But we can call the API endpoint
        import requests
        try:
            res = requests.post("http://web:8000/trigger-fetch")
            if res.status_code == 200:
                st.success("Fetch task triggered!")
            else:
                st.error("Failed to trigger fetch.")
        except Exception as e:
            st.error(f"Failed to contact API: {e}")

    if st.button("Trigger Model Training"):
        import requests
        try:
            res = requests.post("http://web:8000/trigger-train")
            if res.status_code == 200:
                st.success("Training task triggered!")
            else:
                st.error("Failed to trigger training.")
        except Exception as e:
            st.error(f"Failed to contact API: {e}")
