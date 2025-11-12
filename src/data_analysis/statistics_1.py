# Tính toán số liệu

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

print(f"Thư mục gốc Project: {PROJECT_ROOT}")

FLIGHTS_PATH = os.path.join(PROJECT_ROOT, 'data/cleaned/routes_cleaned.csv')
AIRPORTS_PATH = os.path.join(PROJECT_ROOT, 'data/cleaned/airport_db_cleaned.csv')
AIRLINES_PATH = os.path.join(PROJECT_ROOT, 'data/cleaned/airline_db_cleaned.csv') 
GRAPH_JSON_PATH = os.path.join(PROJECT_ROOT, 'data/graph/flight_network.json')
# -------------------------------------------------

COLUMN_MAPPING = {
    'flights': {
        'departure_iata': 'origin_iata',     #
        'arrival_iata': 'destination_iata', #
        'airline_iata': 'airline_iata'      #
    },
    'airports': {
        'iata_code': 'airport_iata',    #
        'airport_name': 'airport_name', #
        'country': 'country'            #
    },
    'airlines': {
        'code_iata_airline': 'airline_iata', # (Từ airline_db_cleaned.csv)
        'name_airline': 'airline_name'       # (Từ airline_db_cleaned.csv)
    }
}

# ----------------------------------------------------------------------
# KHỐI 2: CÁC HÀM TÍNH TOÁN (Đã cập nhật)
# ----------------------------------------------------------------------

def load_csv_data():
    print("Đang tải và xử lý dữ liệu file .csv ...")
    try:
        data_flights = pd.read_csv(FLIGHTS_PATH).rename(columns=COLUMN_MAPPING['flights'])
        data_airports = pd.read_csv(AIRPORTS_PATH).rename(columns=COLUMN_MAPPING['airports'])
        data_airlines = pd.read_csv(AIRLINES_PATH).rename(columns=COLUMN_MAPPING['airlines']) # <-- THÊM LẠI
        
        print("Tải và đổi tên cột .csv thành công.")
        return data_flights, data_airports, data_airlines 
        
    except FileNotFoundError as e:
        print(f"LỖI : Không tìm thấy file .csv. {e}")
        return None, None, None
    except KeyError as e:
        print(f"LỖI : KeyError. Tên cột trong 'COLUMN_MAPPING' không khớp với file .csv.")
        return None, None, None

def get_overview_stats(flights_df, airports_df, airlines_df):
    """Tính thống kê tổng quan."""
    return {
        'total_routes_data': len(flights_df),
        'total_airports_db': len(airports_df),
        'total_airlines_db': len(airlines_df) 
    }

def get_top_airports_by_routes(flights_df, airports_df, top_n=10):
    """Phân tích top airport """
    departures = flights_df['origin_iata'].value_counts()
    arrivals = flights_df['destination_iata'].value_counts()
    total_routes = departures.add(arrivals, fill_value=0).sort_values(ascending=False)
    
    top_airports_df = total_routes.head(top_n).reset_index()
    top_airports_df.columns = ['airport_iata', 'total_routes']
    
    top_airports_full = pd.merge(top_airports_df, airports_df[['airport_iata', 'airport_name']], on='airport_iata', how='left')
    
    top_airports_full['airport_name'] = top_airports_full['airport_name'].fillna(top_airports_full['airport_iata'])
    top_airports_full.index = top_airports_full.index + 1
    return top_airports_full

def get_top_airlines_by_country_coverage(flights_df, airports_df, airlines_df, top_n=10):
    """
    Phân tích Top 10 Hãng bay bay đến nhiều quốc gia khác nhau nhất.
    """
    print("\n Đang tính 'Top Airlines by Country Coverage'...")
    
    # 1. & 2. Lấy dữ liệu cần thiết
    routes_data = flights_df[['airline_iata', 'destination_iata']]
    airports_data = airports_df[['airport_iata', 'country']]
    
    # 3. Merge để lấy (airline_iata, country)
    merged_df = pd.merge(routes_data, airports_data, left_on='destination_iata', right_on='airport_iata', how='left')
    
    # 4. & 5. Đếm số quốc gia duy nhất
    airline_countries = merged_df[['airline_iata', 'country']].drop_duplicates()
    country_count_series = airline_countries.groupby('airline_iata')['country'].count()
    
    # 6. Lấy Top 10 (chỉ có IATA và count)
    top_airlines_df = country_count_series.sort_values(ascending=False).head(top_n).reset_index()
    top_airlines_df.columns = ['airline_iata', 'country_count']
    
    # 7. Lọc file airlines_df
    unique_airlines_df = airlines_df[['airline_iata', 'airline_name']].drop_duplicates(subset=['airline_iata'])

    # 8. Merge Top 10 với file tên
    top_airlines_full = pd.merge(
        top_airlines_df,
        unique_airlines_df, 
        on='airline_iata',
        how='left'
    )
    
    # 9. Fix NaN (nếu có)
    top_airlines_full['airline_name'] = top_airlines_full['airline_name'].fillna(
        top_airlines_full['airline_iata']
    )
    # -----------------------------------------------
    
    top_airlines_full.index = top_airlines_full.index + 1
    return top_airlines_full
# ------------------------------------------

def get_top_important_airports(preprocessed_airports_df, top_n=10):
    """Phân tích Top Hubs bằng cách tải file JSON của TV3 (Giữ nguyên)."""
    print("\n Đang tính 'Top Important Hubs' (từ file JSON)...")
    try:
        with open(GRAPH_JSON_PATH, 'r') as f:
            data = json.load(f)
        
        G = json_graph.node_link_graph(data, directed=True)
        print("Tải file 'flight_network.json' thành công.")
        print("Đang tính Betweenness Centrality...")
        
        centrality_dict = nx.betweenness_centrality(G, weight="weight", normalized=True)
        
        centrality_df = pd.DataFrame(centrality_dict.items(), columns=['airport_iata', 'betweenness_centrality'])
        
        top_hubs_df = centrality_df.sort_values(by='betweenness_centrality', ascending=False).head(top_n)
        
        top_hubs_full = pd.merge(top_hubs_df, preprocessed_airports_df[['airport_iata', 'airport_name']], on='airport_iata', how='left')
        
        top_hubs_full['airport_name'] = top_hubs_full['airport_name'].fillna(top_hubs_full['airport_iata'])
        top_hubs_full.index = top_hubs_full.index + 1
        return top_hubs_full

    except FileNotFoundError:
        print(f"LỖI : Không tìm thấy file .json của TV3 tại: {GRAPH_JSON_PATH}")
        return pd.DataFrame()
    except Exception as e:
        print(f"LỖI : Gặp lỗi khi xử lý file .json. Lỗi: {e}")
        return pd.DataFrame()

# ----------------------------------------------------------------------
# KHỐI 3: CHẠY TEST (Đã cập nhật)
# ----------------------------------------------------------------------
def main_test():
    flights, airports, airlines = load_csv_data() 

    if flights is None or airports is None or airlines is None:
        print("LỖI: Không thể tải dữ liệu .csv. Dừng chương trình test.")
        return

    print("\n Đã tải và chuẩn hóa dữ liệu .csv. Bắt đầu tính toán: ")

    stats = get_overview_stats(flights, airports, airlines) # Truyền cả 3
    print(f"\n Phân tích tổng quan:")
    print(stats)
    
    top_airports = get_top_airports_by_routes(flights, airports)
    print(f"\n Top {len(top_airports)} sân bay (theo số đường bay)")
    print(top_airports)
    
    top_airlines_coverage = get_top_airlines_by_country_coverage(flights, airports, airlines)
    print(f"\n Top {len(top_airlines_coverage)} hãng bay (theo phạm vi hoạt động toàn cầu)")
    print(top_airlines_coverage)
    
    top_hubs = get_top_important_airports(airports)
    print(f"\n Top {len(top_hubs)} sân bay quan trọng nhất (hubs)")
    print(top_hubs)
    
    print("\n Hoàn thành chạy test statistics_1.py")

if __name__ == '__main__':
    if SRC_DIR not in sys.path:
        sys.path.append(SRC_DIR)
    main_test()