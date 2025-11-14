import os
import time
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
# "REALTIME" → làm mới theo chu kỳ từ 2 file raw realtime và vẽ lại bản đồ
MODE = os.environ.get("MODE", "MANUAL")   # có thể override bằng env var
REFRESH_INTERVAL = int(os.environ.get("REFRESH_INTERVAL", "10"))  # giây giữa mỗi lần refresh

def realtime_refresh(flight_csv_path: str, schedules_csv_path: str, cleaned_path: str,
                     interval: int = 10, max_iterations: int = None):
    """
    Poll two provided raw CSV files, merge minimal info and trigger map redraws.
    Quy ước đơn giản: merge theo aircraft.regNumber nếu có, lưu ra cleaned_path.
    Chạy vô hạn cho đến khi KeyboardInterrupt hoặc đạt max_iterations.
    """
    try:
        import pandas as pd
    except Exception as e:
        print(f"Pandas không khả dụng: {e}")
        return

    os.makedirs(os.path.dirname(cleaned_path), exist_ok=True)
    iteration = 0
    print(f"[REALTIME] Starting real-time refresh loop (interval={interval}s)...")
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                print("[REALTIME] Reached max iterations, stopping.")
                break

            if not os.path.exists(flight_csv_path):
                print(f"[REALTIME] Không tìm thấy: {flight_csv_path}")
                time.sleep(interval)
                continue
            if not os.path.exists(schedules_csv_path):
                print(f"[REALTIME] Không tìm thấy: {schedules_csv_path}")
                time.sleep(interval)
                continue

            try:
                df_f = pd.read_csv(flight_csv_path)
            except Exception as e:
                print(f"[REALTIME] Lỗi đọc file flight csv: {e}")
                time.sleep(interval)
                continue

            try:
                df_s = pd.read_csv(schedules_csv_path)
            except Exception as e:
                print(f"[REALTIME] Lỗi đọc file schedules csv: {e}")
                df_s = None

            # Merge đơn giản nếu có cột chung aircraft.regNumber
            try:
                if df_s is not None and 'aircraft.regNumber' in df_f.columns and 'aircraft.regNumber' in df_s.columns:
                    merged = df_f.merge(df_s, on='aircraft.regNumber', how='left', suffixes=('_track', '_sched'))
                else:
                    merged = df_f.copy()
            except Exception as e:
                print(f"[REALTIME] Lỗi khi ghép dữ liệu: {e}")
                merged = df_f.copy()

            try:
                merged.to_csv(cleaned_path, index=False)
                print(f"[REALTIME] Iteration {iteration}: saved merged data to {cleaned_path}")
            except Exception as e:
                print(f"[REALTIME] Không thể lưu file cleaned: {e}")

            # Thử gọi draw_routes: hỗ trợ hàm chấp nhận 1 hoặc 2 tham số
            try:
                # ưu tiên gọi với cleaned_path
                draw_routes(cleaned_path)
                print("[REALTIME] Map drawn from cleaned file.")
            except TypeError:
                try:
                    draw_routes(flight_csv_path, schedules_csv_path)
                    print("[REALTIME] Map drawn from raw flight + schedules files.")
                except Exception as e:
                    print(f"[REALTIME] Vẽ map thất bại: {e}")
            except Exception as e:
                print(f"[REALTIME] Vẽ map thất bại: {e}")

            iteration += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        print("[REALTIME] Stopped by user (KeyboardInterrupt).")

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
            print("Không tìm thấy file cleaned data! (sẽ tiếp tục nếu chạy REALTIME)")
        else:
            print(f"Đang sử dụng dữ liệu đã làm sạch: {cleaned_path}")

    # Nếu chạy chế độ REALTIME, sử dụng hai file live được cung cấp và lặp refresh
    if MODE == "REALTIME":
        flight_live = os.path.join("data", "raw", "flight_tracker_live.csv")
        schedules_live = os.path.join("data", "raw", "realtime_schedules_live.csv")
        if not os.path.exists(os.path.dirname(cleaned_path)):
            os.makedirs(os.path.dirname(cleaned_path), exist_ok=True)
        realtime_refresh(flight_live, schedules_live, cleaned_path, interval=REFRESH_INTERVAL)
        print("REALTIME mode finished.")
        return

    # 3️ BUILD GRAPH (TV3)
    print("Xây dựng đồ thị mạng lưới chuyến bay...")
    if os.path.exists(cleaned_path):
        graph = build_flight_graph(cleaned_path)
    else:
        print("Không có cleaned data để xây dựng đồ thị, bỏ qua bước này.")
        graph = None

    # 4️ ANALYZE DATA (TV6)
    print("Phân tích dữ liệu...")
    if os.path.exists(cleaned_path):
        analyze_data(cleaned_path)
    else:
        print("Không có cleaned data để phân tích, bỏ qua bước này.")

    # 5️ DRAW MAP (TV5)
    print("Vẽ bản đồ các đường bay...")
    try:
        draw_routes(cleaned_path)
        print("Map vẽ xong.")
    except Exception as e:
        print(f"Lỗi khi vẽ map: {e}")

    print("Đã hoàn tất quá trình.")
    print("Đồ thị đã được lưu tại: data/graphs/")
    print("Báo cáo đã được lưu tại: data/reports/")

if __name__ == "__main__":
    main()