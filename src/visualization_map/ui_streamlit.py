# Tạo menu chọn thành phố
import sys
from pathlib import Path
# ensure project root is on sys.path so "src" can be imported
project_root = Path(__file__).resolve().parents[2]  # -> Graph_Network_Project
sys.path.insert(0, str(project_root))

import streamlit as st
import folium
from streamlit_folium import st_folium
from src.visualization_map.ui_helper import load_airports, load_routes, get_city_options, filter_routes_by_city

st.set_page_config(page_title="Flight Network Map", layout="wide")

st.title("🌍 Flight Network Visualization")

airports_df = load_airports()
routes_df = load_routes()
cities = get_city_options(airports_df)

col1, col2 = st.columns(2)
city_from = col1.selectbox("✈️ Thành phố đi", cities)
city_to = col2.selectbox("🏙️ Thành phố đến", cities)

filtered_routes = filter_routes_by_city(routes_df, airports_df, city_from, city_to)

st.write(f"🔹 Số đường bay tìm thấy: {len(filtered_routes)}")

if len(filtered_routes) > 0:
    # Vẽ map trực tiếp
    center_lat = airports_df[airports_df["nameCity"] == city_from]["latitudeAirport"].mean()
    center_lon = airports_df[airports_df["nameCity"] == city_from]["longitudeAirport"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=4, tiles="CartoDB positron")

    # Vẽ đường bay
    for _, r in filtered_routes.iterrows():
        folium.PolyLine(
            [[r["dep_lat"], r["dep_lon"]], [r["arr_lat"], r["arr_lon"]]],
            color="blue", weight=2, opacity=0.7
        ).add_to(m)

    st_folium(m, width=1200, height=700)
else:
    st.warning("Không có đường bay nào giữa hai thành phố này.")
