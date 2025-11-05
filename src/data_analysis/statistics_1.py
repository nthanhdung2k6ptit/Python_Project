# Tính toán số liệu
import pandas as pd
import os

def load_data(file_path):  # Hàm chung để tải dữ liệu CSV và xử lý lỗi FileNotFoundError.
    
    if not os.path.exists(file_path):
        print(f"LỖI : Không tìm thấy file '{file_path}'.")
        return None
    
    return pd.read_csv(file_path)

def get_overview_stats(routes_df): # Nhiệm vụ: Tính thống kê tổng quan: số airports, số routes.
    
    if routes_df is None:
        return {}
        
    num_routes = len(routes_df)
    
    # Gộp 2 cột origin và destination để tìm ra tất cả sân bay duy nhất
    all_airports = pd.concat([routes_df['origin'], routes_df['destination']])
    num_airports = all_airports.nunique()
    
    num_airlines = routes_df['airline_iata'].nunique()
    
    stats = {
        'total_unique_routes': num_routes,
        'total_unique_airports': num_airports,
        'total_unique_airlines': num_airlines
    }
    print(f"Phân tích tổng quan: {stats}")
    return stats

def get_top_airports_by_routes(routes_df, top_n=10): #Nhiệm vụ: Phân tích airport nào có nhiều chuyến bay (đường bay) nhất -> Tính tổng số lần xuất hiện ở cả cột 'origin' và 'destination'.
    
    if routes_df is None:
        return pd.DataFrame(columns=['airport_iata', 'total_routes'])
    
    # Đếm số đường bay đi
    departures = routes_df['origin'].value_counts()
    # Đếm số đường bay đến
    arrivals = routes_df['destination'].value_counts()
    
    # Cộng 2 series này lại (fill_value=0 để sân bay chỉ có đi hoặc đến)
    total_routes_per_airport = departures.add(arrivals, fill_value=0).sort_values(ascending=False)
    
    top_airports_df = total_routes_per_airport.head(top_n).reset_index()
    top_airports_df.columns = ['airport_iata', 'total_routes']
    
    print(f"\n Top {top_n} sân bay (theo số đường bay)")
    print(top_airports_df)
    return top_airports_df

def get_top_airlines_by_routes(routes_df, top_n=10): # Nhiệm vụ: Phân tích airline nào có nhiều routes nhất.
    
    if routes_df is None:
        return pd.DataFrame(columns=['airline_iata', 'route_count'])
        
    top_airlines_df = routes_df['airline_iata'].value_counts().head(top_n).reset_index()
    top_airlines_df.columns = ['airline_iata', 'route_count']
    
    print(f"\n Top {top_n} hãng bay (theo số đường bay)")
    print(top_airlines_df)
    return top_airlines_df

def get_top_important_airports(centrality_file_path, top_n = 10):
    """
    Nhiệm vụ: Tạo bảng top 10 airports quan trọng nhất.
    
    Sử dụng dữ liệu Betweenness Centrality do TV3 tính toán.
    [cite: 3]
    """
    centrality_df = load_data(centrality_file_path)
    
    if centrality_df is None:
        return pd.DataFrame(columns=['airport_iata', 'betweenness_centrality'])
        
    # Giả sử file của TV3 có cột 'airport_iata' và 'betweenness_centrality'
    top_hubs_df = centrality_df.sort_values(by='betweenness_centrality', ascending=False).head(top_n)
    
    print(f"\n Top {top_n} sân bay quan trọng nhất (Hubs)")
    print(top_hubs_df)
    return top_hubs_df

# --- Bạn có thể chạy file này độc lập để test ---
if __name__ == '__main__':
    # Giả lập đường dẫn file
    CLEANED_ROUTES_PATH = 'src/data_analysis/cleaned/routes_clean.csv'
    CENTRALITY_PATH = 'src/data_analysis/graph/airport_centrality.csv'
    
    # Tạo dữ liệu giả để test nếu file không tồn tại
    if not os.path.exists('src/data_analysis/cleaned'):
        os.makedirs('src/data_analysis/cleaned')
        print("Tạo dữ liệu giả cho 'routes_clean.csv'...")
        fake_routes_data = {
            'origin': [
                'SGN', 'SGN', 'SGN', 'SGN', 'SGN', 'SGN', 'SGN', 'HAN', 'HAN', 'HAN', 'HAN', 'HAN', 
                'DAD', 'DAD', 'DAD', 'PQC', 'CXR', 'HPH', 'VCA', 'BKK', 'BKK', 'SIN', 'SIN', 'KUL', 
                'ICN', 'NRT', 'HKG', 'DAD', 'HAN', 'SGN', 'SIN', 'ICN'
            ],
            'destination': [
                'HAN', 'DAD', 'PQC', 'CXR', 'HPH', 'BKK', 'SIN', 'SGN', 'DAD', 'ICN', 'BKK', 'CXR', 
                'SGN', 'HAN', 'ICN', 'SGN', 'HAN', 'SGN', 'HAN', 'SGN', 'ICN', 'SGN', 'KUL', 'SIN', 
                'HAN', 'SGN', 'DAD', 'HKG', 'NRT', 'KUL', 'BKK', 'SGN'
            ],
            'airline_iata': [
                'VN', 'VJ', 'QH', 'VU', 'VN', 'VN', 'SQ', 'VN', 'VJ', 'KE', 'TG', 'VJ', 
                'VN', 'VJ', 'VJ', 'VJ', 'QH', 'VN', 'VJ', 'TG', 'KE', 'SQ', 'VJ', 'SQ', 
                'KE', 'JAL', 'VN', 'VN', 'JAL', 'VJ', 'SQ', 'KE'
            ]
        }
        pd.DataFrame(fake_routes_data).to_csv(CLEANED_ROUTES_PATH, index=False)
        
    if not os.path.exists('src/data_analysis/graph'):
        os.makedirs('src/data_analysis/graph')
        print("Tạo dữ liệu giả cho 'airport_centrality.csv'...")
        airports = ['SGN', 'HAN', 'DAD', 'PQC', 'CXR', 'HPH', 'VCA', 'BKK', 'SIN', 'KUL', 'ICN', 'NRT', 'HKG']
        centrality_scores = [
        0.85,  # SGN
        0.82,  # HAN
        0.55,  # DAD
        0.15,  # PQC
        0.12,  # CXR
        0.10,  # HPH
        0.05,  # VCA
        0.65,  # BKK
        0.78,  # SIN
        0.45,  # KUL
        0.70,  # ICN
        0.30,  # NRT
        0.28   # HKG
        ]
        fake_centrality_data = {
            'airport_iata': airports,
            'betweenness_centrality': centrality_scores
        }
        pd.DataFrame(fake_centrality_data).to_csv(CENTRALITY_PATH, index=False)

    
    print("--- Chạy test cho statistics.py ---")
    df_routes = load_data(CLEANED_ROUTES_PATH)
    
    if df_routes is not None:
        stats = get_overview_stats(df_routes)
        top_airports = get_top_airports_by_routes(df_routes)
        top_airlines = get_top_airlines_by_routes(df_routes)
        top_hubs = get_top_important_airports(CENTRALITY_PATH)