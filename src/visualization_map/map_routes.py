# Folium vẽ bản đồ, routes

import os
import folium # type: ignore
import pandas as pd # pyright: ignore[reportMissingModuleSource]

def draw_routes(
    data_path="data/cleaned/routes_clean.csv",
    save_path="data/reports/map.html",
    city=None,
):
    # Đọc dữ liệu
    df = pd.read_csv(data_path)

    # Lọc theo thành phố nếu cần
    if city:
        df = df[(df["origin"] == city) | (df["destination"] == city)]

    # Kiểm tra các cột cần thiết
    required = {"origin_lat", "origin_lon", "dest_lat", "dest_lon"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in CSV: {missing}")

    # Tạo bản đồ
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

    # Vẽ các tuyến
    for _, row in df.iterrows():
        folium.PolyLine(
            [(row["origin_lat"], row["origin_lon"]), (row["dest_lat"], row["dest_lon"])],
            color="blue",
            weight=1,
            opacity=0.7,
        ).add_to(m)

    # Đánh dấu airports (origin)
    for city_code, lat, lon in zip(df["origin"], df["origin_lat"], df["origin_lon"]):
        folium.CircleMarker(location=[lat, lon], radius=3, color="red", fill=True).add_to(m)

    # (Tùy chọn) Đánh dấu destinations
    for city_code, lat, lon in zip(df["destination"], df["dest_lat"], df["dest_lon"]):
        folium.CircleMarker(location=[lat, lon], radius=3, color="green", fill=True).add_to(m)

    # Tạo thư mục nếu chưa có và lưu
    save_dir = os.path.dirname(save_path) or "."
    os.makedirs(save_dir, exist_ok=True)
    m.save(save_path)

    return m


