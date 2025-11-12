# Biểu đồ (bar, pie, top 10)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# --- Khối Import Logic (Import từ statistics_1.py) ---
try:
    from statistics_1 import (
        load_csv_data, 
        get_top_airports_by_routes, 
        get_top_airlines_by_country_coverage 
    )
    print("Import 'statistics_1.py' thành công.")
except ImportError:
    print("LỖI : Không tìm thấy file 'statistics_1.py'.")
    sys.exit(1)

# --- Cài đặt đường dẫn Output (Lưu vào data/reports) ---
try:
    CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    SRC_DIR = os.path.dirname(CURRENT_FILE_DIR)
    PROJECT_ROOT = os.path.dirname(SRC_DIR)
except NameError:
    PROJECT_ROOT = os.path.abspath('../..')

REPORT_DIR = os.path.join(PROJECT_ROOT, 'data', 'reports')
os.makedirs(REPORT_DIR, exist_ok=True)
# ----------------------------------------------

def setup_charts():
    sns.set_theme(style="whitegrid")
    print(f"Các ảnh biểu đồ sẽ được lưu tại: {REPORT_DIR}")

def plot_top_airports(top_airports_df):
    """Vẽ biểu đồ bar chart top airports."""
    if top_airports_df.empty: return
    
    output_path = os.path.join(REPORT_DIR, 'report_top_10_airports.png')
    
    plt.figure(figsize=(12, 8))
    data_to_plot = top_airports_df.sort_values('total_routes', ascending=False)
    ax = sns.barplot(x='total_routes', y='airport_name', data=data_to_plot, palette='Blues_d')
    ax.set_title('Top 10 sân bay có nhiều đường bay nhất', fontsize=16, pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Đã lưu biểu đồ: {output_path}")
    plt.close()

def plot_top_airlines_by_coverage(top_airlines_df):
    """Vẽ biểu đồ bar chart top airlines (theo độ phủ quốc gia)."""
    if top_airlines_df.empty: return

    output_path = os.path.join(REPORT_DIR, 'report_top_10_airlines_coverage.png')
    
    plt.figure(figsize=(12, 8))
    # Sắp xếp theo 'country_count'
    data_to_plot = top_airlines_df.sort_values('country_count', ascending=False)
    
    # Vẽ biểu đồ với 'country_count' và 'airline_name'
    ax = sns.barplot(x='country_count', y='airline_name', data=data_to_plot, palette='Greens_d')
    ax.set_title('Top 10 hãng bay có mạng lưới quốc tế rộng nhất', fontsize=16, pad=20)
    ax.set_xlabel('Số lượng quốc gia phục vụ', fontsize=12)
    ax.set_ylabel('Hãng hàng không', fontsize=12)
        
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Đã lưu biểu đồ: {output_path}")
    plt.close()

# --- Khối chính để chạy file này ---
if __name__ == '__main__':
    setup_charts()
    
    flights, airports, airlines = load_csv_data() 
    
    if flights is not None:
        print("Bắt đầu vẽ biểu đồ...")
        
        top_airports = get_top_airports_by_routes(flights, airports)
        plot_top_airports(top_airports)
        
        top_airlines_coverage = get_top_airlines_by_country_coverage(flights, airports, airlines) 
        plot_top_airlines_by_coverage(top_airlines_coverage)
        
        print("Hoàn thành file charts.py")
    else:
        print("LỖI : Không thể tải dữ liệu. Dừng lại.")