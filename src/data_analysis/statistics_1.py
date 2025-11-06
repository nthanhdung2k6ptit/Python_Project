# Tính toán số liệu

import pandas as pd
import os
import sys

# ----------------------------------------------------------------------
# KHỐI 1: CÀI ĐẶT ĐƯỜNG DẪN VÀ IMPORT
# ----------------------------------------------------------------------

try:
    # Tự động tìm thư mục gốc của project
    CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    SRC_DIR = os.path.dirname(CURRENT_FILE_DIR)
    PROJECT_ROOT = os.path.dirname(SRC_DIR)
    
    # Thêm thư mục của TV3 vào path để import
    GRAPH_BUILDING_DIR = os.path.join(SRC_DIR, 'graph_building')
    if GRAPH_BUILDING_DIR not in sys.path:
        sys.path.append(GRAPH_BUILDING_DIR)
        
    # Import code của TV3
    from build_graph import build_graph
    from algorithms import betweenness_centrality
    
    TV3_IMPORTED = True
    print("INFO (TV6): Đã import thành công code của TV3.")
except ImportError as e:
    print(f"CẢNH BÁO (TV6): Không thể import code của TV3. Lỗi: {e}")
    TV3_IMPORTED = False

# --- Đường dẫn file NGUYÊN BẢN (từ TV2) ---
FLIGHTS_PATH_RAW = os.path.join(PROJECT_ROOT, 'data/clean/flights_raw_clean.csv')
AIRPORTS_PATH_RAW = os.path.join(PROJECT_ROOT, 'data/clean/airport_db_raw_clean.csv')
AIRLINES_PATH_RAW = os.path.join(PROJECT_ROOT, 'data/clean/airline_db_raw_clean.csv')

# --- (!!! SỬA TÊN CỘT Ở ĐÂY NẾU CẦN !!!) ---
COLUMN_MAPPING = {
    'flights': {
        'departure_iatacode': 'origin_iata',
        'arrival_iatacode': 'destination_iata',
        'airline_iatacode': 'airline_iata'
    },
    'airports': {
        'codeiataairport': 'airport_iata', 
        'nameairport': 'airport_name'      
    },
    'airlines': {
        'codeiataairline': 'airline_iata', 
        'nameairline': 'airline_name'       
    }
}
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# KHỐI 2: CÁC HÀM TÍNH TOÁN (LOGIC CHÍNH)
# ----------------------------------------------------------------------

def load_all_data():
    """Tải và đổi tên cột cho 3 file data chính từ TV2."""
    print("INFO (TV6): Đang tải và xử lý dữ liệu từ TV2...")
    try:
        data_flights = pd.read_csv(FLIGHTS_PATH_RAW).rename(columns=COLUMN_MAPPING['flights'])
        data_airports = pd.read_csv(AIRPORTS_PATH_RAW).rename(columns=COLUMN_MAPPING['airports'])
        data_airlines = pd.read_csv(AIRLINES_PATH_RAW).rename(columns=COLUMN_MAPPING['airlines'])
        
        print("INFO (TV6): Tải và đổi tên cột thành công.")
        return data_flights, data_airports, data_airlines
        
    except FileNotFoundError as e:
        print(f"LỖI (TV6): Không tìm thấy file. {e}")
        return None, None, None
    except KeyError as e:
        print(f"LỖI (TV6): KeyError. Tên cột trong 'COLUMN_MAPPING' không khớp với file CSV.")
        print(f"Tên cột bị lỗi: {e}")
        return None, None, None

def get_overview_stats(flights_df, airports_df, airlines_df):
    """Tính thống kê tổng quan."""
    return {
        'total_routes_data': len(flights_df),
        'total_airports_db': len(airports_df),
        'total_airlines_db': len(airlines_df)
    }

def get_top_airports_by_routes(flights_df, airports_df, top_n=10):
    """Phân tích top airport và merge để LẤY TÊN ĐẦY ĐỦ."""
    departures = flights_df['origin_iata'].value_counts()
    arrivals = flights_df['destination_iata'].value_counts()
    total_routes = departures.add(arrivals, fill_value=0).sort_values(ascending=False)
    
    # Lấy Top N
    top_airports_df = total_routes.head(top_n).reset_index()
    top_airports_df.columns = ['airport_iata', 'total_routes']
    
    # Merge để lấy tên
    top_airports_full = pd.merge(
        top_airports_df,
        airports_df[['airport_iata', 'airport_name']],
        on='airport_iata',
        how='left'
    )
    
    top_airports_full.index = top_airports_full.index + 1
    return top_airports_full

def get_top_airlines_by_routes(flights_df, airlines_df, top_n=10):
    """Phân tích top airline và merge, đã fix lỗi 20 hàng."""
    
    # 1. Lấy Top N IATA codes
    top_airlines_df = flights_df['airline_iata'].value_counts().head(top_n).reset_index() 
    top_airlines_df.columns = ['airline_iata', 'route_count']
    
    # 2. (FIX LỖI 20 HÀNG) Lọc file airlines_df chỉ giữ lại 1 dòng/IATA
    unique_airlines_df = airlines_df[['airline_iata', 'airline_name']].drop_duplicates(subset=['airline_iata'])

    # 3. Merge Top N với file đã lọc
    top_airlines_full = pd.merge(
        top_airlines_df,
        unique_airlines_df, # Dùng file đã lọc
        on='airline_iata',
        how='left'
    )
    
    top_airlines_full.index = top_airlines_full.index + 1
    return top_airlines_full

def get_top_important_airports(preprocessed_airports_df, top_n=10):
    """Tự động gọi code của TV3 để xây dựng graph và tính centrality."""
    if not TV3_IMPORTED:
        print("LỖI (TV6): Bỏ qua 'Top Hubs' vì import code TV3 thất bại.")
        return pd.DataFrame()
        
    try:
        print("INFO (TV6): Đang gọi TV3.build_graph(...) (có thể mất vài giây)")
        G = build_graph(AIRPORTS_PATH_RAW, FLIGHTS_PATH_RAW)
        
        print("INFO (TV6): Graph đã tạo. Đang gọi TV3.betweenness_centrality(...)")
        centrality_dict = betweenness_centrality(G)
        
        # Xử lý kết quả
        centrality_df = pd.DataFrame(centrality_dict.items(), 
                                     columns=['airport_iata', 'betweenness_centrality'])
        
        top_hubs_df = centrality_df.sort_values(by='betweenness_centrality', ascending=False).head(top_n)
        
        # Merge để lấy tên (dùng data đã đổi tên cột)
        top_hubs_full = pd.merge(
            top_hubs_df,
            preprocessed_airports_df[['airport_iata', 'airport_name']],
            on='airport_iata',
            how='left'
        )

        top_hubs_full.index = top_hubs_full.index + 1
        return top_hubs_full

    except Exception as e:
        print(f"LỖI (TV6): Gặp lỗi khi đang chạy code của TV3. Lỗi: {e}")
        return pd.DataFrame()

# ----------------------------------------------------------------------
# KHỐI 3: CHẠY TEST (Chỉ chạy khi mở file này)
# ----------------------------------------------------------------------

def main_test():
    """Hàm test, chỉ chạy khi file này được mở trực tiếp."""
    print("--- Chạy file analysis_stats.py (TV6) ở chế độ test ---")
    
    flights, airports, airlines = load_all_data()
    
    if flights is None:
        print("LỖI: Không thể tải dữ liệu. Dừng chương trình test.")
        return

    print("\n*** Đã tải và chuẩn hóa dữ liệu. Bắt đầu tính toán: ***")
    
    # 1. Chạy thống kê tổng quan
    stats = get_overview_stats(flights, airports, airlines)
    print(f"\n--- Phân tích tổng quan ---")
    print(stats)
    
    # 2. Chạy Top 10 Sân bay (Bận rộn)
    top_airports = get_top_airports_by_routes(flights, airports)
    print(f"\n--- Top {len(top_airports)} Sân bay (theo số đường bay) ---")
    print(top_airports)
    
    # 3. Chạy Top 10 Hãng bay
    top_airlines = get_top_airlines_by_routes(flights, airlines)
    print(f"\n--- Top {len(top_airlines)} Hãng bay (theo số đường bay) ---")
    print(top_airlines)
    
    # 4. Chạy Top 10 Sân bay (Hubs)
    top_hubs = get_top_important_airports(airports)
    print(f"\n--- Top {len(top_hubs)} Sân bay quan trọng nhất (Hubs) ---")
    print(top_hubs)
    
    print("\n--- Hoàn thành chạy test analysis_stats.py ---")

if __name__ == '__main__':
    main_test()