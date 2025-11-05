# Biểu đồ (bar, pie, top 10)

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

# Đường dẫn thư mục để lưu ảnh
REPORT_IMG_DIR = 'src/data_analysis/images'

def setup_charts():
    """Tạo thư mục lưu ảnh nếu chưa có."""
    os.makedirs(REPORT_IMG_DIR, exist_ok=True)
    # Cài đặt style chung cho biểu đồ
    sns.set_theme(style="whitegrid")

def plot_top_airports(top_airports_df):
    """
    Nhiệm vụ: Vẽ biểu đồ bar chart top airports.
    
    """
    if top_airports_df.empty:
        print("LỖI (TV6): Không có dữ liệu top airports để vẽ.")
        return

    output_path = os.path.join(REPORT_IMG_DIR, 'top_10_airports.png')
    
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(
        x='total_routes', 
        y='airport_iata', 
        data=top_airports_df,
        palette='Blues_d'
    )
    ax.set_title('Top 10 Sân bay có nhiều đường bay nhất', fontsize=16, pad=20)
    ax.set_xlabel('Tổng số đường bay (Đi & Đến)', fontsize=12)
    ax.set_ylabel('Mã IATA Sân bay', fontsize=12)
    
    # Thêm giá trị (số) lên trên các thanh bar
    for p in ax.patches:
        ax.annotate(
            f'{int(p.get_width())}', 
            (p.get_width(), p.get_y() + p.get_height() / 2.), 
            ha='left', 
            va='center', 
            xytext=(5, 0), 
            textcoords='offset points'
        )
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Đã lưu biểu đồ top airports tại: {output_path}")
    plt.close()

def plot_top_airlines(top_airlines_df):
    """
    Nhiệm vụ: Vẽ biểu đồ bar chart top airlines.
    
    """
    if top_airlines_df.empty:
        print("LỖI (TV6): Không có dữ liệu top airlines để vẽ.")
        return

    output_path = os.path.join(REPORT_IMG_DIR, 'top_10_airlines.png')
    
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(
        x='route_count', 
        y='airline_iata', 
        data=top_airlines_df,
        palette='Greens_d'
    )
    ax.set_title('Top 10 Hãng bay có nhiều đường bay nhất', fontsize=16, pad=20)
    ax.set_xlabel('Số lượng đường bay', fontsize=12)
    ax.set_ylabel('Mã IATA Hãng bay', fontsize=12)
    
    # Thêm giá trị
    for p in ax.patches:
        ax.annotate(
            f'{int(p.get_width())}', 
            (p.get_width(), p.get_y() + p.get_height() / 2.), 
            ha='left', 
            va='center', 
            xytext=(5, 0), 
            textcoords='offset points'
        )
        
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Đã lưu biểu đồ top airlines tại: {output_path}")
    plt.close()

def plot_airline_market_share(routes_df, top_n=10):
    """
    Nhiệm vụ: Vẽ biểu đồ pie chart thị phần hãng bay.
    
    """
    if routes_df is None or routes_df.empty:
        print("LỖI (TV6): Không có dữ liệu routes để vẽ pie chart.")
        return

    output_path = os.path.join(REPORT_IMG_DIR, 'airline_market_share.png')
    
    airline_counts = routes_df['airline_iata'].value_counts()
    
    # Xử lý: Gộp các hãng bay nhỏ vào "Other"
    if len(airline_counts) > top_n:
        top_airlines_counts = airline_counts.head(top_n).copy()
        other_count = airline_counts.iloc[top_n:].sum()
        if other_count > 0:
            top_airlines_counts['Other'] = other_count
    else:
        top_airlines_counts = airline_counts

    plt.figure(figsize=(10, 10))
    plt.pie(
        top_airlines_counts, 
        labels=top_airlines_counts.index, 
        autopct='%1.1f%%', 
        startangle=140,
        pctdistance=0.85
    )
    plt.title('Thị phần đường bay của các Hãng hàng không', fontsize=16, pad=20)
    plt.axis('equal') # Đảm bảo biểu đồ tròn
    
    # Vẽ 1 vòng tròn ở giữa để làm "Donut Chart" (trông đẹp hơn)
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Đã lưu biểu đồ thị phần tại: {output_path}")
    plt.close()

# --- Bạn có thể chạy file này độc lập để test ---
if __name__ == '__main__':
    # Import các hàm từ statistics để lấy dữ liệu test
    from statistics_1 import load_data, get_top_airports_by_routes, get_top_airlines_by_routes
    
    print("--- Chạy test cho charts.py ---")
    
    # Cài đặt
    setup_charts()
    
    # Đường dẫn (đảm bảo file giả từ statistics.py đã được tạo)
    CLEANED_ROUTES_PATH = 'data/cleaned/routes_clean.csv'
    
    # Tải dữ liệu
    df_routes = load_data(CLEANED_ROUTES_PATH)
    
    if df_routes is not None:
        # Lấy dữ liệu
        top_airports = get_top_airports_by_routes(df_routes)
        top_airlines = get_top_airlines_by_routes(df_routes)
        
        # Vẽ biểu đồ
        plot_top_airports(top_airports)
        plot_top_airlines(top_airlines)
        plot_airline_market_share(df_routes)