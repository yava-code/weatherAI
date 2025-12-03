import sys
sys.path.append('/app')
import streamlit as st
import altair as alt
import pandas as pd
from dashboard.utils import get_data

st.set_page_config(page_title="Analytics", page_icon="bar_chart", layout="wide")

st.title("📊 Historical Analytics")

df = get_data()

if not df.empty:
    st.sidebar.header("Filter Data")
    cities = df["city"].unique().tolist()
    selected_cities = st.sidebar.multiselect("Select Cities", cities, default=cities)

    filtered_df = df[df["city"].isin(selected_cities)]

    st.subheader("Temperature Comparison")
    chart = (
        alt.Chart(filtered_df)
        .mark_area(opacity=0.5)
        .encode(
            x=alt.X("timestamp:T", title="Time"),
            y=alt.Y("temperature:Q", title="Temperature (°C)", scale=alt.Scale(zero=False)),
            color="city:N",
            tooltip=["city", "timestamp", "temperature", "humidity"],
        )
        .properties(height=400)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Humidity vs Temperature")
        scatter = (
            alt.Chart(filtered_df)
            .mark_circle(size=60)
            .encode(
                x="humidity:Q",
                y="temperature:Q",
                color="city:N",
                tooltip=["city", "temperature", "humidity"],
            )
            .interactive()
        )
        st.altair_chart(scatter, use_container_width=True)

    with col2:
        st.subheader("Wind Speed Distribution")
        bar = alt.Chart(filtered_df).mark_bar().encode(
            x=alt.X("wind_speed:Q", bin=True),
            y="count()",
            color="city:N",
        )
        st.altair_chart(bar, use_container_width=True)
else:
    st.warning("No data found for analytics.")
