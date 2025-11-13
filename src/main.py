"""
Main script - Graph Network Project
Author: [Tên bạn] (Team Leader)
"""

import os
from src.graph_building.build_graph import build_flight_graph
from src.visualization_map.map_routes import draw_routes
from src.data_analysis.statistics_1 import analyze_data

# Thêm phần API & Cleaning (nếu ở chế độ AUTO)
try:
    from src.api_fetch.aviation_edge_api import fetch_routes_data
    from src.data_processing.clean_data import clean_routes_data
except ImportError:
    print("Module API hoặc Cleaning chưa sẵn sàng, sẽ bỏ qua khi ở MANUAL mode.")

# ==============================
# CHỌN CHẾ ĐỘ CHẠY
# ==============================
# "AUTO" → chạy toàn bộ pipeline (API → Clean → Graph → Map → Reprot)
# "MANUAL" → chỉ dùng data có sẵn (bỏ qua API và cleaning)
MODE = "MANUAL"   # đổi thành "AUTO" nếu muốn demo full

# ==============================
# PIPELINE CHÍNH
# ==============================
def main():
    print("\nGraph Network Project Starting...")
    print(f" Running mode: {MODE}\n")

    raw_path = "data/raw/routes_raw.json"
    cleaned_path = "data/cleaned/routes_clean.csv"

    # 1️ FETCH DATA (TV1)
    if MODE == "AUTO":
        print("🔹 Step 1: Fetching data from Aviation Edge API...")
        try:
            fetch_routes_data(save_path=raw_path)
            print(f"Data saved: {raw_path}")
        except Exception as e:
            print(f"Lỗi khi gọi API: {e}")
            return
    else:
        print("Skipping API fetching (using existing data)")

    # 2️ CLEAN DATA (TV2)
    if MODE == "AUTO":
        print("🔹 Step 2: Cleaning data...")
        try:
            clean_routes_data(input_path=raw_path, output_path=cleaned_path)
            print(f"Cleaned data saved: {cleaned_path}")
        except Exception as e:
            print(f"Lỗi khi làm sạch dữ liệu: {e}")
            return
    else:
        if not os.path.exists(cleaned_path):
            print("Không tìm thấy file cleaned data!")
            return
        print(f"Using existing cleaned data: {cleaned_path}")

    # 3️ BUILD GRAPH (TV3)
    print("🔹 Step 3: Building flight network graph...")
    graph = build_flight_graph(cleaned_path)

    # 4️ ANALYZE DATA (TV6)
    print("🔹 Step 4: Analyzing data...")
    analyze_data(cleaned_path)

    # 5️ DRAW MAP (TV5)
    print("🔹 Step 5: Drawing flight map...")
    draw_routes(cleaned_path)

    #  KẾT THÚC
    print("\nPipeline completed successfully!")
    print("Graph saved in: data/graphs/")
    print("Reports saved in: data/reports/")
    print("To open web UI, run: streamlit run src/visualization_map/ui_streamlit.py")

if __name__ == "__main__":
    main()
