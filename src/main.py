#  Điểm khởi đầu chạy toàn project
import streamlit as st
from src.visualization_map.map_routes import draw_flight_map

# ví dụ: khi nhấn nút “Vẽ bản đồ”
if st.button("✈️ Vẽ bản đồ từ dữ liệu cleaned"):
    draw_flight_map(
        "data/cleaned/airport_db_cleaned.csv",
        "data/cleaned/routes_cleaned.csv"
    )
    st.success("✅ Đã tạo bản đồ thành công! Xem trong data/reports/")

if __name__ == "__main__":
    # chạy thử trực tiếp
    draw_flight_map(
        airports_file="data/cleaned/airport_db_cleaned.csv",
        routes_file="data/cleaned/routes_cleaned.csv",
        save_path="data/reports/test_flight_map.html"
    )
