# Xuất PDF, Excel

import pandas as pd
import os
import sys

# Khối Import Logic (Import từ statistics_1.py)
try:
    from statistics_1 import (
        load_csv_data, 
        get_overview_stats,
        get_top_airports_by_routes, 
        get_top_airlines_by_country_coverage,
        get_top_important_airports
    )
    print("INFO (TV6-Export): Import 'statistics_1.py' thành công.")
except ImportError:
    print("LỖI (TV6-Export): Không tìm thấy file 'statistics_1.py'.")
    sys.exit(1)

# Cài đặt đường dẫn Output
try:
    CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    SRC_DIR = os.path.dirname(CURRENT_FILE_DIR)
    PROJECT_ROOT = os.path.dirname(SRC_DIR)
except NameError:
    PROJECT_ROOT = os.path.abspath('../..')

REPORT_DIR = os.path.join(PROJECT_ROOT, 'data', 'reports')
os.makedirs(REPORT_DIR, exist_ok=True)
REPORT_FILE_PATH_XLSX = os.path.join(REPORT_DIR, 'statistical_report.xlsx')

TRANSLATIONS = {
    'overview': {
        'total_routes_data': 'Tổng số đường bay',
        'total_airports_db': 'Tổng số sân bay',
        'total_airlines_db': 'Tổng số hãng bay'
    },
    'airports': {
        'airport_iata': 'Mã IATA sân bay',
        'total_routes': 'Tổng số đường bay',
        'airport_name': 'Tên sân bay'
    },
    'airlines': {
        'airline_iata': 'Mã IATA hãng bay',
        'country_count': 'Số lượng quốc gia',
        'airline_name': 'Tên hãng bay'
    },
    'hubs': {
        'airport_iata': 'Mã IATA sân bay',
        'betweenness_centrality': 'Điểm Centrality',
        'airport_name': 'Tên sân bay'
    }
}

def auto_adjust_columns(worksheet):
    """Tự động điều chỉnh độ rộng cột trong Excel."""
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
    
    print(f"Đang xuất báo cáo ra file Excel tại: {REPORT_FILE_PATH_XLSX}")
    try:
        with pd.ExcelWriter(REPORT_FILE_PATH_XLSX, engine='openpyxl') as writer:
            
            # Sheet 1: Tổng quan
            overview_df = pd.DataFrame.from_dict(stats_dict, orient='index', columns=['Số lượng'])
            overview_df.index.name = "Hạng mục"
            overview_df.to_excel(writer, sheet_name='Tổng quan', index_label = 'Hạng mục')
            auto_adjust_columns(writer.sheets['Tổng quan']) 
            
            # Sheet 2: Top sân bay theo số đường bay
            if not top_airports_df.empty:
                top_airports_df.to_excel(writer, sheet_name='Top sân bay (đường bay)', index_label="STT")
                auto_adjust_columns(writer.sheets['Top sân bay (đường bay)'])
            
            # Sheet 3: Top Hãng bay (Độ phủ)
            if not top_airlines_df.empty:
                top_airlines_df.to_excel(writer, sheet_name='Top hãng bay (mức độ hoạt động toàn cầu)', index_label="STT")
                auto_adjust_columns(writer.sheets['Top hãng bay (mức độ hoạt động toàn cầu)'])
                
            # Sheet 4: Top Sân bay (Hubs)
            if not top_hubs_df.empty:
                top_hubs_df.to_excel(writer, sheet_name='Top sân bay (Hubs)', index_label="STT") # Dịch tên sheet
                
                # Lấy worksheet
                worksheet4 = writer.sheets['Top sân bay (Hubs)']
                
                target_col_name = TRANSLATIONS['hubs']['betweenness_centrality']
                target_col_letter = ''
                for col_idx, col_name in enumerate(top_hubs_df.columns, 1):
                    if col_name == target_col_name:
                        target_col_letter = worksheet4.cell(row=1, column=col_idx + 1).column_letter
                        break
                
                if target_col_letter:
                    for cell in worksheet4[target_col_letter][1:]: 
                        cell.number_format = '0.000000'
                
                auto_adjust_columns(worksheet4)
            
        print(f"\nĐã xuất báo cáo Excel thành công!")
    
    except PermissionError:
        print(f"LỖI : Không thể ghi file Excel. File '{REPORT_FILE_PATH_XLSX}' có thể đang được mở.")
    except Exception as e:
        print(f"LỖI : Không thể ghi file Excel. Lỗi: {e}")


# Khối chính để chạy file này 
if __name__ == '__main__':
    flights, airports, airlines = load_csv_data() 
    
    if flights is not None:
        print("INFO : Đang tính toán tất cả số liệu...")
        
        stats = get_overview_stats(flights, airports, airlines) 
        top_airports = get_top_airports_by_routes(flights, airports)
        top_airlines_coverage = get_top_airlines_by_country_coverage(flights, airports, airlines) 
        top_hubs = get_top_important_airports(airports)
        
        if not top_hubs.empty:
            top_hubs['betweenness_centrality'] = top_hubs['betweenness_centrality'].round(6)
        
        stats = {TRANSLATIONS['overview'].get(k, k): v for k, v in stats.items()}
        top_airports = top_airports.rename(columns=TRANSLATIONS['airports'])
        top_airlines_coverage = top_airlines_coverage.rename(columns=TRANSLATIONS['airlines'])
        top_hubs = top_hubs.rename(columns=TRANSLATIONS['hubs'])
        # ------------------------------------

        # Gọi hàm xuất file đã Việt hóa
        export_to_excel(stats, top_airports, top_airlines_coverage, top_hubs)
        
        print("Hoàn thành file export_report.py")
    else:
        print("LỖI : Không thể tải dữ liệu. Dừng lại.")