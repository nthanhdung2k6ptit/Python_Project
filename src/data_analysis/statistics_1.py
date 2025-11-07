# Tính toán số liệu

import pandas as pd
import os
import json 
import networkx as nx 
from networkx.readwrite import json_graph 

# ----------------------------------------------------------------------
# KHỐI 1: CÀI ĐẶT ĐƯỜNG DẪN VÀ TÊN CỘT
# ----------------------------------------------------------------------

# Tự động tìm thư mục gốc của project
try:
    CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    SRC_DIR = os.path.dirname(CURRENT_FILE_DIR)
    PROJECT_ROOT = os.path.dirname(SRC_DIR)
except NameError:
    # Xử lý nếu chạy trong môi trường không có __file__
    PROJECT_ROOT = os.path.abspath('.')
    print("CẢNH BÁO (TV6): Không thể tự động tìm PROJECT_ROOT, giả định là thư mục hiện tại.")

print(f"INFO (TV6): Thư mục gốc Project: {PROJECT_ROOT}")

# --- Đường dẫn file NGUYÊN BẢN (từ TV2 và TV3) ---
FLIGHTS_PATH = os.path.join(PROJECT_ROOT, 'data/clean/flights_raw_clean.csv')
AIRPORTS_PATH = os.path.join(PROJECT_ROOT, 'data/clean/airport_db_raw_clean.csv')
AIRLINES_PATH = os.path.join(PROJECT_ROOT, 'data/clean/airline_db_raw_clean.csv')
GRAPH_JSON_PATH = os.path.join(PROJECT_ROOT, 'data/graph/flight_network.json') # <-- (MỚI)

# --- (Kiểm tra lại tên cột ở đây) ---
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
# KHỐI 2: CÁC HÀM TÍNH TOÁN
# ----------------------------------------------------------------------

def load_csv_data():
    """Tải và đổi tên cột cho 3 file data chính từ TV2."""
    print("INFO (TV6): Đang tải và xử lý dữ liệu CSV từ TV2...")
    try:
        data_flights = pd.read_csv(FLIGHTS_PATH).rename(columns=COLUMN_MAPPING['flights'])
        data_airports = pd.read_csv(AIRPORTS_PATH).rename(columns=COLUMN_MAPPING['airports'])
        data_airlines = pd.read_csv(AIRLINES_PATH).rename(columns=COLUMN_MAPPING['airlines'])
        
        print("INFO (TV6): Tải và đổi tên cột CSV thành công.")
        return data_flights, data_airports, data_airlines
        
    except FileNotFoundError as e:
        print(f"LỖI (TV6): Không tìm thấy file CSV. {e}")
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
    """Phân tích top airport (Bận rộn) và fix lỗi NaN."""
    departures = flights_df['origin_iata'].value_counts()
    arrivals = flights_df['destination_iata'].value_counts()
    total_routes = departures.add(arrivals, fill_value=0).sort_values(ascending=False)
    
    top_airports_df = total_routes.head(top_n).reset_index()
    top_airports_df.columns = ['airport_iata', 'total_routes']
    
    top_airports_full = pd.merge(
        top_airports_df,
        airports_df[['airport_iata', 'airport_name']],
        on='airport_iata',
        how='left'
    )
    
    # (FIX LỖI NaN)
    top_airports_full['airport_name'] = top_airports_full['airport_name'].fillna(
        top_airports_full['airport_iata']
    )
    top_airports_full.index = top_airports_full.index + 1
    return top_airports_full

def get_top_airlines_by_routes(flights_df, airlines_df, top_n=10):
    """Phân tích top airline, đã fix lỗi 20 hàng và lỗi NaN."""
    top_airlines_df = flights_df['airline_iata'].value_counts().head(top_n).reset_index() 
    top_airlines_df.columns = ['airline_iata', 'route_count']
    
    # (FIX LỖI 20 HÀNG)
    unique_airlines_df = airlines_df[['airline_iata', 'airline_name']].drop_duplicates(subset=['airline_iata'])

    top_airlines_full = pd.merge(
        top_airlines_df,
        unique_airlines_df, 
        on='airline_iata',
        how='left'
    )
    
    # (FIX LỖI NaN)
    top_airlines_full['airline_name'] = top_airlines_full['airline_name'].fillna(
        top_airlines_full['airline_iata']
    )
    top_airlines_full.index = top_airlines_full.index + 1
    return top_airlines_full

# --- (!!! HÀM ĐÃ ĐƯỢC VIẾT LẠI HOÀN TOÀN !!!) ---
def get_top_important_airports(preprocessed_airports_df, top_n=10):
    """
    Phân tích Top Hubs bằng cách tải file JSON của TV3 và tự tính centrality.
    """
    print("\nINFO (TV6): Đang tính 'Top Important Hubs' (từ file JSON)...")
    try:
        # 1. Mở file JSON của TV3
        with open(GRAPH_JSON_PATH, 'r') as f:
            data = json.load(f)
        
        # 2. Tải file JSON vào đồ thị NetworkX
        # (directed=True vì file JSON của TV3 có "directed": true)
        G = json_graph.node_link_graph(data, directed=True)
        print("INFO (TV6): Tải file 'flight_network.json' thành công.")

        # 3. Tự tính Betweenness Centrality
        # (Chúng ta vẫn cần thư viện 'networkx' - pip install networkx)
        print("INFO (TV6): Graph đã tải. Đang tính Betweenness Centrality (có thể mất vài giây)...")
        # Giả sử TV3 đã thêm 'weight' vào graph, nếu không, hãy xóa 'weight="weight"'
        centrality_dict = nx.betweenness_centrality(G, weight="weight", normalized=True)
        
        # 4. Xử lý kết quả (như cũ)
        print("INFO (TV6): Đã tính xong. Đang xử lý kết quả...")
        centrality_df = pd.DataFrame(centrality_dict.items(), 
                                     columns=['airport_iata', 'betweenness_centrality'])
        
        top_hubs_df = centrality_df.sort_values(by='betweenness_centrality', ascending=False).head(top_n)
        
        top_hubs_full = pd.merge(
            top_hubs_df,
            preprocessed_airports_df[['airport_iata', 'airport_name']],
            on='airport_iata',
            how='left'
        )
        
        # (FIX LỖI NaN)
        top_hubs_full['airport_name'] = top_hubs_full['airport_name'].fillna(
            top_hubs_full['airport_iata']
        )
        top_hubs_full.index = top_hubs_full.index + 1
        return top_hubs_full

    except FileNotFoundError:
        print(f"LỖI (TV6): Không tìm thấy file JSON của TV3 tại: {GRAPH_JSON_PATH}")
        return pd.DataFrame()
    except ImportError:
        print("LỖI (TV6): Thiếu thư viện 'networkx'. Hãy chạy 'pip install networkx'")
        return pd.DataFrame()
    except Exception as e:
        print(f"LỖI (TV6): Gặp lỗi khi xử lý file JSON. Lỗi: {e}")
        return pd.DataFrame()

# ----------------------------------------------------------------------
# KHỐI 3: CHẠY TEST (Chỉ chạy khi mở file này)
# ----------------------------------------------------------------------

def main_test():
    """Hàm test, chỉ chạy khi file này được mở trực tiếp."""
    print("--- Chạy file analysis_stats.py (TV6) ở chế độ test ---")
    
    flights, airports, airlines = load_csv_data()
    
    if flights is None:
        print("LỖI: Không thể tải dữ liệu CSV. Dừng chương trình test.")
        return

    print("\n*** Đã tải và chuẩn hóa dữ liệu CSV. Bắt đầu tính toán: ***")
    
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
    
    # 4. Chạy Top 10 Sân bay (Hubs) - BẰNG CÁCH MỚI
    top_hubs = get_top_important_airports(airports)
    print(f"\n--- Top {len(top_hubs)} Sân bay quan trọng nhất (Hubs) ---")
    print(top_hubs)
    
    print("\n--- Hoàn thành chạy test analysis_stats.py ---")

if __name__ == '__main__':
    main_test()