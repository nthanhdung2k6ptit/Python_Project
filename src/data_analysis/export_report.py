# Xuất PDF, Excel

import pandas as pd
import os
import sys

# --- Khối Import Logic ---
try:
    # Import tất cả các hàm cần thiết
    from statistics_1 import (
        load_csv_data, 
        get_overview_stats,
        get_top_airports_by_routes, 
        get_top_airlines_by_routes,
        get_top_important_airports
    )
    print("INFO (TV6-Export): Import 'statistics_1.py' thành công.")
except ImportError:
    print("LỖI (TV6-Export): Không tìm thấy file 'statistics_1.py'.")
    print("Hãy đảm bảo file 'statistics_1.py' của bạn nằm cùng thư mục.")
    sys.exit(1) # Dừng chương trình

# --- Cài đặt đường dẫn ---
# Lưu file Excel vào chính thư mục này
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_FILE_PATH = os.path.join(CURRENT_DIR, 'statistical_report.xlsx')

def export_to_excel(stats_dict, top_airports_df, top_airlines_df, top_hubs_df):
    """Xuất tất cả kết quả ra file Excel."""
    
    print(f"INFO (TV6-Export): Đang xuất báo cáo ra file Excel tại: {REPORT_FILE_PATH}")
    
    try:
        # Sử dụng 'openpyxl' (cần pip install openpyxl)
        with pd.ExcelWriter(REPORT_FILE_PATH, engine='openpyxl') as writer:
            
            # Sheet 1: Tổng quan
            overview_df = pd.DataFrame.from_dict(stats_dict, orient='index', columns=['Value'])
            overview_df.to_excel(writer, sheet_name='Tong_Quan')
            
            # Sheet 2: Top Sân bay (Bận rộn)
            # index=False để không lưu cột số thứ tự (1-10)
            if not top_airports_df.empty:
                top_airports_df.to_excel(writer, sheet_name='Top_Airports_by_Routes', index=False)
            
            # Sheet 3: Top Hãng bay
            if not top_airlines_df.empty:
                top_airlines_df.to_excel(writer, sheet_name='Top_Airlines_by_Routes', index=False)
                
            # Sheet 4: Top Sân bay (Hubs)
            if not top_hubs_df.empty:
                top_hubs_df.to_excel(writer, sheet_name='Top_Airport_Hubs_Centrality', index=False)
            
        print(f"\nĐã xuất báo cáo Excel thành công!")
    
    except PermissionError:
        print(f"LỖI (TV6-Export): Không thể ghi file Excel. File '{REPORT_FILE_PATH}' có thể đang được mở. Hãy đóng file lại và thử.")
    except Exception as e:
        print(f"LỖI (TV6-Export): Không thể ghi file Excel. Lỗi: {e}")
        print("Hãy đảm bảo bạn đã cài thư viện 'openpyxl' (pip install openpyxl)")

# --- Khối chính để chạy file này ---
if __name__ == '__main__':
    print("--- Chạy file export_report.py (TV6) ---")
    
    # Tải 3 file CSV
    flights, airports, airlines = load_csv_data()
    
    if flights is not None:
        print("INFO (TV6-Export): Đang tính toán tất cả số liệu...")
        
        # --- Chạy TOÀN BỘ phân tích ---
        stats = get_overview_stats(flights, airports, airlines)
        top_airports = get_top_airports_by_routes(flights, airports)
        top_airlines = get_top_airlines_by_routes(flights, airlines)
        top_hubs = get_top_important_airports(airports)
        
        # --- Xuất file ---
        export_to_excel(stats, top_airports, top_airlines, top_hubs)
        
        print("--- Hoàn thành file export_report.py (TV6) ---")
    else:
        print("LỖI (TV6-Export): Không thể tải dữ liệu. Dừng lại.")