import os
import pandas as pd
import psycopg2
import streamlit as st

def get_data():
    dsn = os.getenv("DATABASE_URL", "postgresql://meteo:meteo_pass@db/meteo_mind")
    try:
        conn = psycopg2.connect(dsn)
        query = "SELECT city, timestamp, temperature, humidity, wind_speed FROM weather_measurements ORDER BY timestamp DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Connection error: {e}")
        return pd.DataFrame()
