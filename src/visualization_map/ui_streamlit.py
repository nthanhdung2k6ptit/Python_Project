# Tạo menu chọn thành phố

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[2]  # Graph_Network_Project
sys.path.insert(0, str(project_root))

import streamlit as st
from streamlit_folium import folium_static
from src.visualization_map.map_routes import create_flight_map
from src.visualization_map.ui_helper import load_airports
import pandas as pd

st.set_page_config(page_title="🛫 Group 3 | Flight Network", layout="wide")
st.title("🛫 Flight Network - Real Routes Visualization")

# safe load (avoid truth-value on DataFrame)
_df_airports = load_airports()
if _df_airports is None:
    df_airports = pd.DataFrame()
else:
    df_airports = _df_airports

# helper: pick first existing column from candidates, return Series of strings
def _pick_col_series(df, candidates):
    for c in candidates:
        if c in df.columns:
            return df[c].fillna("").astype(str)
    # return empty-string series with correct length
    return pd.Series([""] * len(df), index=df.index)

airport_options = []
if not df_airports.empty:
    iata = _pick_col_series(df_airports, ['iata_code', 'IATA', 'departureiata', 'codeiataairport'])
    name = _pick_col_series(df_airports, ['airport_name', 'name'])
    country = _pick_col_series(df_airports, ['country', 'iso_country'])
    airport_options = (iata + " - " + name + " (" + country + ")").tolist()

airport_choices = [""] + airport_options
selected_airport = st.selectbox("Chọn sân bay khởi hành (hoặc để trống):", airport_choices)
select_iata = selected_airport.split(" - ")[0] if selected_airport else None

if st.button("Hiển thị đường bay"):
    st.info(f"Đang hiển thị các đường bay xuất phát từ {select_iata or 'TOÀN CẦU'} ...")
    m = create_flight_map(departure_filter=select_iata)
    folium_static(m)
    st.success("Đã hiển thị bản đồ thành công!")