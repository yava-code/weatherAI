import sys
sys.path.append('/app')
import streamlit as st
import httpx
import os
import redis
import psycopg2

st.set_page_config(page_title="MeteoMind Enterprise", page_icon="⚡", layout="wide")

st.title("⚡ MeteoMind: Enterprise Weather Intelligence")
st.markdown("Type a city and run on-demand analysis.")

city = st.text_input("Enter City Name", "London")
run = st.button("Analyze")
if run and city:
    try:
        with httpx.Client() as c:
            resp = c.post("http://web:8000/analyze", json={"city_name": city}, timeout=60)
        st.session_state["analysis"] = resp.json()
        st.switch_page("pages/1_City_Intelligence.py")
    except Exception as e:
        st.error(str(e))

st.divider()
st.markdown("Or open Global Monitor for cached insights.")
st.page_link("pages/2_Global_Monitor.py", label="Open Global Monitor")

st.sidebar.header("System Status")
db_ok = False
redis_ok = False
try:
    dsn = os.getenv("DATABASE_URL", "postgresql://meteo:meteo_pass@db/meteo_mind")
    conn = psycopg2.connect(dsn)
    conn.close()
    db_ok = True
except Exception:
    db_ok = False
try:
    rurl = os.getenv("REDIS_URL", "redis://redis:6379/0")
    r = redis.Redis.from_url(rurl)
    r.ping()
    redis_ok = True
except Exception:
    redis_ok = False
if db_ok:
    st.sidebar.success("DB Connected")
else:
    st.sidebar.error("DB Unavailable")
if redis_ok:
    st.sidebar.success("Redis Connected")
else:
    st.sidebar.error("Redis Unavailable")

st.caption("Powered by MeteoMind Engine v1.0")
