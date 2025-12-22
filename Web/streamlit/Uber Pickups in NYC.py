# app.py
import streamlit as st
import pandas as pd
import numpy as np

# 제목(원본 데모 느낌 유지)
st.title("Uber Pickups in NYC")

DATE_COLUMN = "date/time"
DATA_URL = (
    "https://s3-us-west-2.amazonaws.com/"
    "streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)

# 최신 Streamlit 권장: st.cache_data 사용
@st.cache_data
def load_data(nrows: int) -> pd.DataFrame:
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data.columns = [str(c).lower() for c in data.columns]
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data_load_state = st.text("Loading data...")
data = load_data(10000)
data_load_state.text("Done! (using st.cache_data)")

if st.checkbox("Show raw data"):
    st.subheader("Raw data")
    st.write(data)

st.subheader("Number of pickups by hour")
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
st.bar_chart(hist_values)

hour_to_filter = st.slider("hour", 0, 23, 17)
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

st.subheader(f"Map of all pickups at {hour_to_filter}:00")
st.map(filtered_data)
