# Xuất PDF, Excel
# src/analysis/export_report.py

import pandas as pd
import os
import sys

# --- Khối Import Logic (Import từ statistics_1.py) ---
try:
    from statistics_1 import (
        load_csv_data, 
        get_overview_stats,
        get_top_airports_by_routes, 
        get_top_airlines_by_country_coverage,
        get_top_important_airports
    )
    print("Import 'statistics_1.py' thành công.")
except ImportError:
    print("LỖI : Không tìm thấy file 'statistics_1.py'.")
    sys.exit(1)

# --- Cài đặt đường dẫn Output ---
try:
    CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    SRC_DIR = os.path.dirname(CURRENT_FILE_DIR)
    PROJECT_ROOT = os.path.dirname(SRC_DIR)
except NameError:
    PROJECT_ROOT = os.path.abspath('../..')

REPORT_DIR = os.path.join(PROJECT_ROOT, 'data', 'reports')
os.makedirs(REPORT_DIR, exist_ok=True)
REPORT_FILE_PATH_XLSX = os.path.join(REPORT_DIR, 'statistical_report.xlsx')
# ----------------------------------------------

# --- Hàm tự động căn chỉnh ---
def auto_adjust_columns(worksheet):
    """Tự động căn chỉnh độ rộng của tất cả các cột trong một worksheet."""
    for col in worksheet.columns:
        max_length = 0
        column_letter = col[0].column_letter 
        for cell in col:
            if cell.value:
                current_length = len(str(cell.value))
                if current_length > max_length:
                    max_length = current_length
        adjusted_width = max_length + 2
        worksheet.column_dimensions[column_letter].width = adjusted_width

def export_to_excel(stats_dict, top_airports_df, top_airlines_df, top_hubs_df):
    """Xuất tất cả kết quả ra file Excel VÀ TỰ CĂN CHỈNH."""
    
    print(f"Đang xuất báo cáo ra file Excel tại: {REPORT_FILE_PATH_XLSX}")
    try:
        with pd.ExcelWriter(REPORT_FILE_PATH_XLSX, engine='openpyxl') as writer:
            
            # Sheet 1: Tổng quan
            overview_df = pd.DataFrame.from_dict(stats_dict, orient='index', columns=['Value'])
            overview_df.to_excel(writer, sheet_name='Tong_Quan')
            auto_adjust_columns(writer.sheets['Tong_Quan']) 
            
            # Sheet 2: Top Sân bay (Bận rộn)
            if not top_airports_df.empty:
                top_airports_df.to_excel(writer, sheet_name='Top_Airports_by_Routes', index=False)
                auto_adjust_columns(writer.sheets['Top_Airports_by_Routes'])
            
            # Sheet 3: Top Hãng bay (Độ phủ)
            if not top_airlines_df.empty:
                top_airlines_df.to_excel(writer, sheet_name='Top_Airlines_by_Coverage', index=False)
                auto_adjust_columns(writer.sheets['Top_Airlines_by_Coverage'])
                
            # Sheet 4: Top Sân bay (Hubs)
            if not top_hubs_df.empty:
                top_hubs_df.to_excel(writer, sheet_name='Top_Airport_Hubs_Centrality', index=False)
                
                # --- (!!! SỬA LỖI Ở ĐÂY !!!) ---
                # Lấy worksheet
                worksheet4 = writer.sheets['Top_Airport_Hubs_Centrality']
                
                # Tìm chữ cái của cột 'betweenness_centrality'
                target_col_letter = ''
                for col_idx, col_name in enumerate(top_hubs_df.columns, 1):
                    if col_name == 'betweenness_centrality':
                        # Lấy chữ cái (ví dụ: 'B') từ đối tượng cell
                        target_col_letter = worksheet4.cell(row=1, column=col_idx).column_letter
                        break
                
                # Áp dụng định dạng 6 chữ số thập phân cho cột đó
                if target_col_letter:
                    # Lặp qua tất cả các ô trong cột đó (bỏ qua header)
                    for cell in worksheet4[target_col_letter][1:]: 
                        cell.number_format = '0.000000'

                # Chạy căn chỉnh cột (sau khi đã định dạng)
                auto_adjust_columns(worksheet4)
            
        print(f"\nĐã xuất báo cáo Excel (đã tự căn chỉnh và định dạng) thành công!")
    
    except PermissionError:
        print(f"LỖI : Không thể ghi file Excel. File '{REPORT_FILE_PATH_XLSX}' có thể đang được mở.")
    except Exception as e:
        print(f"LỖI : Không thể ghi file Excel. Lỗi: {e}")

# --- Khối chính để chạy file này (Giữ nguyên) ---
if __name__ == '__main__':
    
    flights, airports, airlines = load_csv_data() 
    
    if flights is not None:
        print("Đang tính toán tất cả số liệu...")
        
        stats = get_overview_stats(flights, airports, airlines) 
        top_airports = get_top_airports_by_routes(flights, airports)
        top_airlines_coverage = get_top_airlines_by_country_coverage(flights, airports, airlines) 
        top_hubs = get_top_important_airports(airports)
        
        # (LÀM TRÒN SỐ TRONG PANDAS)
        if not top_hubs.empty:
            top_hubs['betweenness_centrality'] = top_hubs['betweenness_centrality'].round(6)
        
        export_to_excel(stats, top_airports, top_airlines_coverage, top_hubs)
        
        print("Hoàn thành file export_report.py")
    else:
        print("LỖI : Không thể tải dữ liệu. Dừng lại.")