# Xuất PDF, Excel

# src/data_analysis/export_report.py

import pandas as pd
import os

REPORT_FILE_PATH = 'src/data_analysis/reports/statistical_report.xlsx'

def export_to_excel(stats_dict, top_airports_df, top_airlines_df, top_hubs_df):
    """
    Nhiệm vụ: Xuất báo cáo ra file Excel.
    
    Mỗi DataFrame sẽ là một sheet riêng.
    """
    # Đảm bảo thư mục 'data/reports' tồn tại
    os.makedirs(os.path.dirname(REPORT_FILE_PATH), exist_ok=True)
    
    try:
        with pd.ExcelWriter(REPORT_FILE_PATH, engine='openpyxl') as writer:
            # Sheet 1: Tổng quan
            overview_df = pd.DataFrame.from_dict(stats_dict, orient='index', columns=['Value'])
            overview_df.to_excel(writer, sheet_name='Tong_Quan')
            
            # Sheet 2: Top Sân bay (theo đường bay)
            if not top_airports_df.empty:
                top_airports_df.to_excel(writer, sheet_name='Top_Airports_by_Routes', index=False)
            
            # Sheet 3: Top Hãng bay
            if not top_airlines_df.empty:
                top_airlines_df.to_excel(writer, sheet_name='Top_Airlines_by_Routes', index=False)
                
            # Sheet 4: Top Sân bay (Hubs quan trọng)
            if not top_hubs_df.empty:
                top_hubs_df.to_excel(writer, sheet_name='Top_Airport_Hubs_Centrality', index=False)
            
        print(f"\nĐã xuất báo cáo Excel thành công tại: {REPORT_FILE_PATH}")
    
    except Exception as e:
        print(f"LỖI (TV6): Không thể ghi file Excel. Lỗi: {e}")
        print("Hãy đảm bảo bạn đã cài thư viện 'openpyxl' (pip install openpyxl)")

# --- Bạn có thể chạy file này độc lập để test ---
if __name__ == '__main__':
    # Import các hàm từ statistics để lấy dữ liệu test
    from statistics_1 import load_data, get_overview_stats, get_top_airports_by_routes, get_top_airlines_by_routes, get_top_important_airports

    print("--- Chạy test cho export_report.py ---")
    
    # Đường dẫn (đảm bảo file giả từ statistics.py đã được tạo)
    CLEANED_ROUTES_PATH = 'src/data_analysis/cleaned/routes_clean.csv'
    CENTRALITY_PATH = 'src/data_analysis/graph/airport_centrality.csv'

    # Tải và tính toán
    df_routes = load_data(CLEANED_ROUTES_PATH)
    if df_routes is not None:
        stats = get_overview_stats(df_routes)
        top_airports = get_top_airports_by_routes(df_routes)
        top_airlines = get_top_airlines_by_routes(df_routes)
        top_hubs = get_top_important_airports(CENTRALITY_PATH)
        
    # Xuất file
    export_to_excel(stats, top_airports, top_airlines, top_hubs)