import streamlit as st
from dashboard.utils import get_data

st.set_page_config(
    page_title="MeteoMind Enterprise",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ MeteoMind: Enterprise Weather Intelligence")
st.markdown("### System Status & Global Overview")

df = get_data()

if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    total_records = len(df)
    cities_tracked = df["city"].nunique()
    latest_temp = df.iloc[0]["temperature"]
    last_update = df["timestamp"].max()

    col1.metric("Data Points", f"{total_records}", "+12/hr")
    col2.metric("Cities Tracked", f"{cities_tracked}", "Active")
    col3.metric("Latest Temp (Global)", f"{latest_temp:.1f}°C")
    col4.metric("Last Sync", str(last_update.strftime("%H:%M:%S")))

    st.divider()
    st.info("System is running normally. Worker nodes collect data hourly from Open-Meteo API.")
    st.subheader("Recent Data Ingestion Log")
    st.dataframe(df.head(10), use_container_width=True)
else:
    st.warning("No data found. Please wait for the initial ingestion cycle.")
