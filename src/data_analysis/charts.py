# Biểu đồ (bar, pie, top 10)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# --- Khối Import Logic ---
try:
    from statistics_1 import (
        load_csv_data, 
        get_top_airports_by_routes, 
        get_top_airlines_by_routes
    )
    print("INFO (TV6-Charts): Import 'statistics_1.py' thành công.")
except ImportError:
    print("LỖI (TV6-Charts): Không tìm thấy file 'statistics_1.py'.")
    sys.exit(1)

# --- Cài đặt đường dẫn Output ---
try:
    CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    SRC_DIR = os.path.dirname(CURRENT_FILE_DIR)
    PROJECT_ROOT = os.path.dirname(SRC_DIR)
except NameError:
    PROJECT_ROOT = os.path.abspath('../..')

REPORT_DIR = os.path.join(PROJECT_ROOT, 'data', 'report')
os.makedirs(REPORT_DIR, exist_ok=True)

def setup_charts():
    sns.set_theme(style="whitegrid")
    print(f"INFO (TV6-Charts): Các ảnh biểu đồ sẽ được lưu tại: {REPORT_DIR}")

def plot_top_airports(top_airports_df):
    """Vẽ biểu đồ bar chart top airports."""
    if top_airports_df.empty: return
    
    output_path = os.path.join(REPORT_DIR, 'report_top_10_airports.png')
    
    plt.figure(figsize=(12, 8))
    data_to_plot = top_airports_df.sort_values('total_routes', ascending=False)
    ax = sns.barplot(x='total_routes', y='airport_name', data=data_to_plot, palette='Blues_d')
    ax.set_title('Top 10 Sân bay có nhiều đường bay nhất', fontsize=16, pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Đã lưu biểu đồ: {output_path}")
    plt.close()

def plot_top_airlines(top_airlines_df):
    """Vẽ biểu đồ bar chart top airlines (chỉ có IATA)."""
    if top_airlines_df.empty: return

    output_path = os.path.join(REPORT_DIR, 'report_top_10_airlines.png')
    
    plt.figure(figsize=(12, 8))
    data_to_plot = top_airlines_df.sort_values('route_count', ascending=False)
    
    # --- (ĐÃ SỬA) ---
    # Vẽ biểu đồ với 'airline_iata' thay vì 'airline_name'
    ax = sns.barplot(x='route_count', y='airline_iata', data=data_to_plot, palette='Greens_d')
    ax.set_title('Top 10 Hãng bay có nhiều đường bay nhất', fontsize=16, pad=20)
    ax.set_ylabel('Mã IATA Hãng bay', fontsize=12) # Sửa nhãn
    # ---------------
        
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Đã lưu biểu đồ: {output_path}")
    plt.close()

# --- Khối chính để chạy file này ---
if __name__ == '__main__':
    print("--- Chạy file charts.py (TV6) ---")
    setup_charts()
    
    flights, airports, airlines = load_csv_data() # airlines sẽ là None
    
    if flights is not None:
        print("INFO (TV6-Charts): Bắt đầu vẽ biểu đồ...")
        
        top_airports = get_top_airports_by_routes(flights, airports)
        plot_top_airports(top_airports)
        
        top_airlines = get_top_airlines_by_routes(flights) # Không cần 'airlines'
        plot_top_airlines(top_airlines)
        
        print("--- Hoàn thành file charts.py (TV6) ---")
    else:
        print("LỖI (TV6-Charts): Không thể tải dữ liệu. Dừng lại.")