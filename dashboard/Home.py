import streamlit as st
import httpx

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
