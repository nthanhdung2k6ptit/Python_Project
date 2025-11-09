# Xuất PDF, Excel

import pandas as pd
import os
import sys

# --- Khối Import Logic ---
try:
    # Import từ file 'statistics_1.py' của bạn
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
    sys.exit(1)


# --- Cài đặt đường dẫn Output (Theo cấu trúc file mới) ---
try:
    CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    SRC_DIR = os.path.dirname(CURRENT_FILE_DIR)
    PROJECT_ROOT = os.path.dirname(SRC_DIR)
except NameError:
    PROJECT_ROOT = os.path.abspath('../..')

REPORT_DIR = os.path.join(PROJECT_ROOT, 'data', 'report')
os.makedirs(REPORT_DIR, exist_ok=True)
REPORT_FILE_PATH = os.path.join(REPORT_DIR, 'statistical_report.xlsx')
# ----------------------------------------------


# --- (!!! HÀM MỚI ĐỂ TỰ ĐỘNG CĂN CHỈNH !!!) ---
def auto_adjust_columns(worksheet):
    """
    Tự động căn chỉnh độ rộng của tất cả các cột trong một worksheet.
    """
    print(f"INFO (TV6-Export): Đang tự căn chỉnh cột cho sheet '{worksheet.title}'...")
    # Lặp qua tất cả các cột trong worksheet
    for col in worksheet.columns:
        max_length = 0
        column_letter = col[0].column_letter # Lấy tên cột (ví dụ: 'A', 'B')
        
        # Lặp qua tất cả các cell trong cột
        for cell in col:
            # Bỏ qua cell trống
            if cell.value:
                # Tìm độ dài lớn nhất (cả header và dữ liệu)
                current_length = len(str(cell.value))
                if current_length > max_length:
                    max_length = current_length
        
        # Đặt độ rộng mới cho cột (thêm 2 đơn vị để đệm)
        adjusted_width = max_length + 2
        worksheet.column_dimensions[column_letter].width = adjusted_width
# ----------------------------------------------


def export_to_excel(stats_dict, top_airports_df, top_airlines_df, top_hubs_df):
    """Xuất tất cả kết quả ra file Excel VÀ TỰ CĂN CHỈNH."""
    
    print(f"INFO (TV6-Export): Đang xuất báo cáo ra file Excel tại: {REPORT_FILE_PATH}")
    
    try:
        with pd.ExcelWriter(REPORT_FILE_PATH, engine='openpyxl') as writer:
            
            # --- Sheet 1: Tổng quan ---
            overview_df = pd.DataFrame.from_dict(stats_dict, orient='index', columns=['Value'])
            overview_df.to_excel(writer, sheet_name='Tong_Quan')
            # Lấy worksheet và căn chỉnh
            worksheet1 = writer.sheets['Tong_Quan']
            auto_adjust_columns(worksheet1) # <-- GỌI HÀM CĂN CHỈNH
            
            # --- Sheet 2: Top Sân bay (Bận rộn) ---
            if not top_airports_df.empty:
                top_airports_df.to_excel(writer, sheet_name='Top_Airports_by_Routes', index=False)
                # Lấy worksheet và căn chỉnh
                worksheet2 = writer.sheets['Top_Airports_by_Routes']
                auto_adjust_columns(worksheet2) # <-- GỌI HÀM CĂN CHỈNH
            
            # --- Sheet 3: Top Hãng bay ---
            if not top_airlines_df.empty:
                top_airlines_df.to_excel(writer, sheet_name='Top_Airlines_by_Routes', index=False)
                # Lấy worksheet và căn chỉnh
                worksheet3 = writer.sheets['Top_Airlines_by_Routes']
                auto_adjust_columns(worksheet3) # <-- GỌI HÀM CĂN CHỈNH
                
            # --- Sheet 4: Top Sân bay (Hubs) ---
            if not top_hubs_df.empty:
                top_hubs_df.to_excel(writer, sheet_name='Top_Airport_Hubs_Centrality', index=False)
                # Lấy worksheet và căn chỉnh
                worksheet4 = writer.sheets['Top_Airport_Hubs_Centrality']
                auto_adjust_columns(worksheet4) # <-- GỌI HÀM CĂN CHỈNH
            
        print(f"\nĐã xuất báo cáo Excel (đã tự căn chỉnh) thành công!")
    
    except PermissionError:
        print(f"LỖI (TV6-Export): Không thể ghi file Excel. File '{REPORT_FILE_PATH}' có thể đang được mở.")
    except Exception as e:
        print(f"LỖI (TV6-Export): Không thể ghi file Excel. Lỗi: {e}")

# --- Khối chính để chạy file này (Giữ nguyên) ---
if __name__ == '__main__':
    print("--- Chạy file export_report.py (TV6) ---")
    
    flights, airports, airlines = load_csv_data()
    
    if flights is not None:
        print("INFO (TV6-Export): Đang tính toán tất cả số liệu...")
        
        stats = get_overview_stats(flights, airports) 
        top_airports = get_top_airports_by_routes(flights, airports)
        top_airlines = get_top_airlines_by_routes(flights) 
        top_hubs = get_top_important_airports(airports)
        
        export_to_excel(stats, top_airports, top_airlines, top_hubs)
        
        print("--- Hoàn thành file export_report.py (TV6) ---")
    else:
        print("LỖI (TV6-Export): Không thể tải dữ liệu. Dừng lại.")