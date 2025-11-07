# Biểu đồ (bar, pie, top 10)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# --- Khối Import Logic ---
# Cố gắng import từ file logic của bạn
try:
    from statistics_1 import (
        load_csv_data, # Sửa lại tên hàm load
        get_top_airports_by_routes, 
        get_top_airlines_by_routes
    )
    print("INFO (TV6-Charts): Import 'statistics_1.py' thành công.")
except ImportError:
    print("LỖI (TV6-Charts): Không tìm thấy file 'statistics_1.py'.")
    print("Hãy đảm bảo file 'statistics_1.py' của bạn nằm cùng thư mục.")
    sys.exit(1) # Dừng chương trình

# --- Cài đặt đường dẫn ---
# Lưu file ảnh vào chính thư mục này
REPORT_IMG_DIR = os.path.dirname(os.path.abspath(__file__))

def setup_charts():
    """Cài đặt style chung cho biểu đồ."""
    sns.set_theme(style="whitegrid")
    print(f"INFO (TV6-Charts): Các ảnh biểu đồ sẽ được lưu tại: {REPORT_IMG_DIR}")

def plot_top_airports(top_airports_df):
    """Vẽ biểu đồ bar chart top airports."""
    if top_airports_df.empty:
        return

    y_column = 'airport_name' # Dùng cột 'airport_name' đã được fix NaN
    output_path = os.path.join(REPORT_IMG_DIR, 'report_top_10_airports.png')
    
    plt.figure(figsize=(12, 8))
    # Sắp xếp lại dữ liệu để bar chart đẹp hơn
    data_to_plot = top_airports_df.sort_values('total_routes', ascending=False)
    
    ax = sns.barplot(x='total_routes', y=y_column, data=data_to_plot, palette='Blues_d')
    ax.set_title('Top 10 Sân bay có nhiều đường bay nhất', fontsize=16, pad=20)
    ax.set_xlabel('Tổng số đường bay (Đi & Đến)', fontsize=12)
    ax.set_ylabel('Sân bay', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Đã lưu biểu đồ: {output_path}")
    plt.close()

def plot_top_airlines(top_airlines_df):
    """Vẽ biểu đồ bar chart top airlines."""
    if top_airlines_df.empty:
        return

    y_column = 'airline_name' # Dùng cột 'airline_name' đã được fix NaN
    output_path = os.path.join(REPORT_IMG_DIR, 'report_top_10_airlines.png')
    
    plt.figure(figsize=(12, 8))
    # Sắp xếp lại dữ liệu
    data_to_plot = top_airlines_df.sort_values('route_count', ascending=False)
    
    ax = sns.barplot(x='route_count', y=y_column, data=data_to_plot, palette='Greens_d')
    ax.set_title('Top 10 Hãng bay có nhiều đường bay nhất', fontsize=16, pad=20)
    ax.set_xlabel('Số lượng đường bay', fontsize=12)
    ax.set_ylabel('Hãng hàng không', fontsize=12)
        
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Đã lưu biểu đồ: {output_path}")
    plt.close()

# --- Khối chính để chạy file này ---
if __name__ == '__main__':
    print("--- Chạy file charts.py (TV6) ---")
    
    setup_charts()
    
    # Tải 3 file CSV
    flights, airports, airlines = load_csv_data()
    
    if flights is not None:
        print("INFO (TV6-Charts): Bắt đầu vẽ biểu đồ...")
        
        # 1. Vẽ Top Sân Bay
        top_airports = get_top_airports_by_routes(flights, airports)
        plot_top_airports(top_airports)
        
        # 2. Vẽ Top Hãng Bay
        top_airlines = get_top_airlines_by_routes(flights, airlines)
        plot_top_airlines(top_airlines)
        
        print("--- Hoàn thành file charts.py (TV6) ---")
    else:
        print("LỖI (TV6-Charts): Không thể tải dữ liệu. Dừng lại.")