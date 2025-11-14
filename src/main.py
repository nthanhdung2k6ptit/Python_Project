
import os
from src.graph_building.build_graph import build_flight_graph
from src.visualization_map.map_routes import draw_routes
from src.data_analysis.statistics_1 import analyze_data

# Thêm phần API & Cleaning (nếu ở chế độ AUTO)
try:
    from api_fetch.aviation_edge_api_vn import fetch_routes_data
    from src.data_processing.clean_data import clean_routes_data
except ImportError:
    print("Module API hoặc Cleaning chưa sẵn sàng, sẽ bỏ qua khi ở MANUAL mode.")

# ==============================
# CHỌN CHẾ ĐỘ CHẠY
# ==============================
# "AUTO" → chạy toàn bộ pipeline (API → Clean → Graph → Map → Reprot)
# "MANUAL" → chỉ dùng data có sẵn (bỏ qua API và cleaning)
MODE = "MANUAL"   # đổi thành "AUTO" nếu muốn demo full

def main():
    print("\nGraph Network Project Starting...")
    print(f" Running mode: {MODE}\n")

    raw_path = "data/raw/_raw.json"
    cleaned_path = "data/cleaned/routes_clean.csv"

    # 1️ FETCH DATA (TV1)
    if MODE == "AUTO":
        print("Lấy dữ liệu từ API")
        try:
            fetch_routes_data(save_path=raw_path)
            print(f"Dữ liệu đã lưu: {raw_path}")
        except Exception as e:
            print(f"Lỗi khi gọi API: {e}")
            return
    else:
        print("Bỏ qua bước lấy dữ liệu từ API (dùng dữ liệu có sẵn)")

    # 2️ CLEAN DATA (TV2)
    if MODE == "AUTO":
        print("Làm sạch dữ liệu")
        try:
            clean_routes_data(input_path=raw_path, output_path=cleaned_path)
            print(f"Dữ liệu đã được làm sạch và lưu tại: {cleaned_path}")
        except Exception as e:
            print(f"Lỗi khi làm sạch dữ liệu: {e}")
            return
    else:
        if not os.path.exists(cleaned_path):
            print("Không tìm thấy file cleaned data!")
            return
        print(f"Đang sử dụng dữ liệu đã làm sạch: {cleaned_path}")
    # 3️ BUILD GRAPH (TV3)
    print("Xây dựng đồ thị mạng lưới chuyến bay...")
    graph = build_flight_graph(cleaned_path)

    # 4️ ANALYZE DATA (TV6)
    print("Phân tích dữ liệu...")
    analyze_data(cleaned_path)

    # 5️ DRAW MAP (TV5)
    print("Vẽ bản đồ các đường bay...")
    draw_routes(cleaned_path)

    print("Đã hoàn tất quá trình.")
    print("Đồ thị đã được lưu tại: data/graphs/")
    print("Báo cáo đã được lưu tại: data/reports/")

if __name__ == "__main__":
    main()
