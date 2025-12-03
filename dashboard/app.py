import os
import pandas as pd
import psycopg2
import streamlit as st

st.set_page_config(page_title="MeteoMind Dashboard", layout="wide")
st.title("MeteoMind Dashboard")

dsn = os.getenv("DATABASE_URL", "postgresql://meteo:meteo_pass@db/meteo_mind")
conn = psycopg2.connect(dsn)
df = pd.read_sql_query(
    "SELECT city, timestamp, temperature, humidity, wind_speed FROM weather_measurements ORDER BY timestamp DESC LIMIT 100",
    conn,
)
st.dataframe(df)
