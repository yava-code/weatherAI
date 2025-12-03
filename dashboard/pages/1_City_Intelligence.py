import sys
sys.path.append('/app')
import streamlit as st
import altair as alt
import pandas as pd

st.set_page_config(page_title="City Intelligence", page_icon="cityscape", layout="wide")

data = st.session_state.get("analysis")
if not data:
    st.warning("No analysis found. Go to Home and run Analyze.")
else:
    city = data.get("city")
    st.title(f"City Intelligence: {city}")
    cur = data.get("current") or {}
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Temp", f"{cur.get('temperature', 'n/a')} °C")
    c2.metric("Humidity", f"{cur.get('humidity', 'n/a')} %")
    c3.metric("Wind", f"{cur.get('wind_speed', 'n/a')} m/s")

    preds = data.get("predictions") or []
    df = pd.DataFrame(preds)
    if not df.empty:
        df_chart = df.copy()
        chart = (
            alt.Chart(df_chart)
            .mark_area(opacity=0.6)
            .encode(
                x=alt.X("hour:Q", title="Hours Ahead"),
                y=alt.Y("temperature:Q", title="Predicted Temperature (°C)"),
                tooltip=["hour", "temperature"],
            )
            .properties(height=320)
        )
        st.subheader("24h Forecast")
        st.altair_chart(chart, use_container_width=True)

    metrics = data.get("metrics") or {}
    fi = metrics.get("feature_importance") or {}
    if fi:
        st.subheader("Feature Importance")
        fi_df = pd.DataFrame({"Feature": list(fi.keys()), "Importance": list(fi.values())}).sort_values(by="Importance", ascending=False)
        fi_chart = alt.Chart(fi_df).mark_bar().encode(
            x=alt.X("Importance", axis=None),
            y=alt.Y("Feature", sort="-x"),
            color=alt.Color("Importance", scale=alt.Scale(scheme="greens")),
            tooltip=["Feature", "Importance"],
        ).properties(height=240)
        st.altair_chart(fi_chart, use_container_width=True)
