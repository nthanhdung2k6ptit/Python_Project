# Tạo menu chọn thành phố

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[2]  # Graph_Network_Project
sys.path.insert(0, str(project_root))

import streamlit as st
from streamlit_folium import folium_static
from src.visualization_map.map_routes import create_flight_map
from src.visualization_map.ui_helper import load_airports, load_cities
import pandas as pd

st.set_page_config(page_title="🛫 Group 3 | Flight Network", layout="wide")
st.title("🛫 Flight Network - Real Routes Visualization")

# safe load (avoid truth-value on DataFrame)
_df_airports = load_airports()
if _df_airports is None:
    df_airports = pd.DataFrame()
else:
    df_airports = _df_airports

# Load cities
_df_cities = load_cities()
if _df_cities is None:
    df_cities = pd.DataFrame()
else:
    df_cities = _df_cities

# Build city -> list of iatas mapping
city_map = {}
if not df_cities.empty:
    # city_iata may contain single IATA or comma-separated list; normalize to list
    for _, r in df_cities.iterrows():
        city = r['city_name'].strip()
        iata_field = "" if pd.isna(r.get('city_iata', "")) else str(r.get('city_iata', ""))
        iata_list = [s.strip() for s in iata_field.replace(';',',').split(',') if s.strip()] if iata_field else []
        city_map.setdefault(city, []).extend(iata_list)
    # deduplicate lists
    for k in list(city_map.keys()):
        city_map[k] = sorted(set([i.upper() for i in city_map[k] if i]))

city_options = [""] + sorted(city_map.keys())

selected_city = st.selectbox("Chọn thành phố khởi hành (để trống cũng được):", city_options)
selected_iatas = city_map.get(selected_city, []) if selected_city else []

if st.button("Hiển thị đường bay"):
    st.info(f"Đang hiển thị các đường bay xuất phát từ thành phố {selected_city or 'TOÀN CẦU'} ...")
    # pass list of IATA codes to map generator
    m = create_flight_map(departure_city_iatas = selected_iatas)
    folium_static(m)
    st.success("Đã hiển thị bản đồ thành công <3")