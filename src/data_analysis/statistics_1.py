# Tính toán số liệu
# src/analysis/statistics_1.py

import pandas as pd
import os
import json
import networkx as nx
from networkx.readwrite import json_graph
import sys

# ----------------------------------------------------------------------
# KHỐI 1: CÀI ĐẶT ĐƯỜNG DẪN VÀ TÊN CỘT
# ----------------------------------------------------------------------
try:
    CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    SRC_DIR = os.path.dirname(CURRENT_FILE_DIR)
    PROJECT_ROOT = os.path.dirname(SRC_DIR)
except NameError:
    PROJECT_ROOT = os.path.abspath('../..')

print(f"INFO (TV6): Thư mục gốc Project: {PROJECT_ROOT}")

# --- (ĐÃ CẬP NHẬT TÊN FILE MỚI) ---
FLIGHTS_PATH = os.path.join(PROJECT_ROOT, 'data/cleaned/routes_cleaned.csv')
AIRPORTS_PATH = os.path.join(PROJECT_ROOT, 'data/cleaned/airport_db_cleaned.csv')
GRAPH_JSON_PATH = os.path.join(PROJECT_ROOT, 'data/graph/flight_network.json')
# (Không có file airlines_clean.csv)
# -------------------------------------------------

# --- (ĐÃ CẬP NHẬT TÊN CỘT THEO FILE MỚI) ---
COLUMN_MAPPING = {
    'flights': {
        'departure_iata': 'origin_iata',     #
        'arrival_iata': 'destination_iata', #
        'airline_iata': 'airline_iata'      #
    },
    'airports': {
        'iata_code': 'airport_iata',    #
        'airport_name': 'airport_name'  #
    }
    # (Không có mapping cho airlines)
}
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# KHỐI 2: CÁC HÀM TÍNH TOÁN
# ----------------------------------------------------------------------

def load_csv_data():
    """Tải và đổi tên cột cho 2 file data chính từ TV2."""
    print("INFO (TV6): Đang tải và xử lý dữ liệu CSV từ TV2...")
    try:
        data_flights = pd.read_csv(FLIGHTS_PATH).rename(columns=COLUMN_MAPPING['flights'])
        data_airports = pd.read_csv(AIRPORTS_PATH).rename(columns=COLUMN_MAPPING['airports'])
        
        print("INFO (TV6): Tải và đổi tên cột CSV thành công.")
        # Trả về flights và airports. (airlines = None)
        return data_flights, data_airports, None
        
    except FileNotFoundError as e:
        print(f"LỖI (TV6): Không tìm thấy file CSV. {e}")
        return None, None, None
    except KeyError as e:
        print(f"LỖI (TV6): KeyError. Tên cột trong 'COLUMN_MAPPING' không khớp với file CSV.")
        print(f"Tên cột bị lỗi: {e}")
        return None, None, None

def get_overview_stats(flights_df, airports_df):
    """Tính thống kê tổng quan."""
    stats = {
        'total_routes_data': len(flights_df),
        'total_airports_db': len(airports_df),
        'total_unique_airlines': flights_df['airline_iata'].nunique() # Đếm từ file routes
    }
    return stats

def get_top_airports_by_routes(flights_df, airports_df, top_n=10):
    """Phân tích top airport (Bận rộn) và fix lỗi NaN."""
    departures = flights_df['origin_iata'].value_counts()
    arrivals = flights_df['destination_iata'].value_counts()
    total_routes = departures.add(arrivals, fill_value=0).sort_values(ascending=False)
    
    top_airports_df = total_routes.head(top_n).reset_index()
    top_airports_df.columns = ['airport_iata', 'total_routes']
    
    top_airports_full = pd.merge(top_airports_df, airports_df[['airport_iata', 'airport_name']], on='airport_iata', how='left')
    
    top_airports_full['airport_name'] = top_airports_full['airport_name'].fillna(top_airports_full['airport_iata'])
    top_airports_full.index = top_airports_full.index + 1
    return top_airports_full

def get_top_airlines_by_routes(flights_df, top_n=10):
    """Phân tích top airline (Chỉ có IATA code)."""
    top_airlines_df = flights_df['airline_iata'].value_counts().head(top_n).reset_index() 
    top_airlines_df.columns = ['airline_iata', 'route_count']
    
    top_airlines_df.index = top_airlines_df.index + 1
    return top_airlines_df

def get_top_important_airports(preprocessed_airports_df, top_n=10):
    """Phân tích Top Hubs bằng cách tải file JSON của TV3."""
    print("\nINFO (TV6): Đang tính 'Top Important Hubs' (từ file JSON)...")
    try:
        with open(GRAPH_JSON_PATH, 'r') as f:
            data = json.load(f)
        
        G = json_graph.node_link_graph(data, directed=True)
        print("INFO (TV6): Tải file 'flight_network.json' thành công.")
        print("INFO (TV6): Đang tính Betweenness Centrality (có thể mất vài giây)...")
        
        centrality_dict = nx.betweenness_centrality(G, weight="weight", normalized=True)
        
        print("INFO (TV6): Đã tính xong. Đang xử lý kết quả...")
        centrality_df = pd.DataFrame(centrality_dict.items(), columns=['airport_iata', 'betweenness_centrality'])
        
        top_hubs_df = centrality_df.sort_values(by='betweenness_centrality', ascending=False).head(top_n)
        
        top_hubs_full = pd.merge(top_hubs_df, preprocessed_airports_df[['airport_iata', 'airport_name']], on='airport_iata', how='left')
        
        top_hubs_full['airport_name'] = top_hubs_full['airport_name'].fillna(top_hubs_full['airport_iata'])
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
# KHỐI 3: CHẠY TEST
# ----------------------------------------------------------------------
def main_test():
    """Hàm test, chỉ chạy khi file này được mở trực tiếp."""
    print("--- Chạy file statistics_1.py (TV6) ở chế độ test ---")
    
    flights, airports, airlines = load_csv_data()
    
    if flights is None:
        print("LỖI: Không thể tải dữ liệu CSV. Dừng chương trình test.")
        return

    print("\n*** Đã tải và chuẩn hóa dữ liệu CSV. Bắt đầu tính toán: ***")
    
    stats = get_overview_stats(flights, airports)
    print(f"\n--- Phân tích tổng quan ---")
    print(stats)
    
    top_airports = get_top_airports_by_routes(flights, airports)
    print(f"\n--- Top {len(top_airports)} Sân bay (theo số đường bay) ---")
    print(top_airports)
    
    top_airlines = get_top_airlines_by_routes(flights) # Không cần 'airlines'
    print(f"\n--- Top {len(top_airlines)} Hãng bay (theo số đường bay) ---")
    print(top_airlines)
    
    top_hubs = get_top_important_airports(airports)
    print(f"\n--- Top {len(top_hubs)} Sân bay quan trọng nhất (Hubs) ---")
    print(top_hubs)
    
    print("\n--- Hoàn thành chạy test statistics_1.py ---")

if __name__ == '__main__':
    # Thêm code để xử lý import cho cấu trúc thư mục mới
    if SRC_DIR not in sys.path:
        sys.path.append(SRC_DIR)
    main_test()