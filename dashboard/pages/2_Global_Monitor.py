import sys
sys.path.append('/app')
import os
import json
import streamlit as st
import redis

st.set_page_config(page_title="Global Monitor", page_icon="globe", layout="wide")

rurl = os.getenv("REDIS_URL", "redis://redis:6379/0")
r = redis.Redis.from_url(rurl)
keys = [k.decode() for k in r.keys("city_intel:*")]

st.title("Global Monitor")
if not keys:
    st.info("No cached cities yet.")
else:
    cols = st.columns(3)
    i = 0
    for key in keys:
        raw = r.get(key)
        if not raw:
            continue
        data = json.loads(raw)
        city = data.get("city")
        preds = data.get("predictions") or []
        latest = preds[-1]["temperature"] if preds else "n/a"
        cols[i % 3].metric(city, f"{latest} °C")
        i += 1
