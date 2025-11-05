import json
import pandas as pd
import matplotlib.pyplot as plt
import os

#  1. Đọc file CSV và tạo từ điển tra cứu tọa độ 


# Đường dẫn file CSV 
csv_file_path = os.path.join('data', 'clean', 'airport_db_raw_clean.csv')
coords_map = {}

try:
    df_airports = pd.read_csv(csv_file_path)
    
    # Tạo một từ điển (dictionary) để tra cứu nhanh
    # key = codeiataairport, value = {lat, lon}
    coords_map = df_airports.set_index('codeiataairport')[
        ['latitudeairport', 'longitudeairport']
    ].to_dict('index')
    
    print(f"Đã tạo từ điển tra cứu cho {len(coords_map)} sân bay từ file CSV.")

except FileNotFoundError:
    print(f"LỖI: Không tìm thấy file CSV tại: '{csv_file_path}'")
    print("Hãy đảm bảo bạn đang chạy script này từ thư mục gốc 'Graph_Network_Project'.")
except Exception as e:
    print(f"LỖI khi đọc file CSV: {e}")


# --- 2. Đọc file JSON và trích xuất dữ liệu ---

# Đường dẫn file JSON
json_file_path = os.path.join('data', 'graph', 'flight_network.json')
airport_nodes = []

try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data_object = json.load(f)
        # Lấy danh sách sân bay từ key "nodes"
        airport_nodes = data_object.get('nodes')
        
    if not isinstance(airport_nodes, list):
        print("Lỗi: Không tìm thấy key 'nodes' trong file JSON.")
        airport_nodes = []
    else:
        print(f"Đã đọc thành công {len(airport_nodes)} nodes từ file JSON.")

except FileNotFoundError:
    print(f"LỖI: Không tìm thấy file JSON tại '{json_file_path}'.")
except Exception as e:
    print(f"LỖI khi đọc file JSON: {e}")


# --- 3. Kết hợp dữ liệu và chuẩn bị vẽ ---

regular_lons = []  # Kinh độ (sân bay thường)
regular_lats = []  # Vĩ độ (sân bay thường)
hub_lons = []      # Kinh độ (Hub)
hub_lats = []      # Vĩ độ (Hub)
airports_not_found = []

if airport_nodes and coords_map:
    for airport in airport_nodes:
        try:
            # Lấy IATA code từ file JSON (giả định key là 'id')
            iata_code = airport.get('id')
            
            # Tra cứu tọa độ từ bản đồ CSV
            coords = coords_map.get(iata_code)
            
            if coords:
                # Lấy lon/lat từ CỘT ĐÚNG trong file CSV
                lon = coords['longitudeairport']
                lat = coords['latitudeairport']
                
                # Phân loại sân bay Hub
                if airport.get('hub') == 1.0 or airport.get('hub') is True:
                    hub_lons.append(lon)
                    hub_lats.append(lat)
                else:
                    regular_lons.append(lon)
                    regular_lats.append(lat)
            else:
                airports_not_found.append(iata_code)

        except KeyError as e:
            print(f"LỖI: Dữ liệu JSON hoặc CSV thiếu key cần thiết: {e}")
        except Exception as e:
            print(f"LỖI xử lý node {airport.get('id')}: {e}")

    print(f"\nĐã xử lý xong. Sẵn sàng để vẽ:")
    print(f"  - {len(regular_lons)} sân bay thường")
    print(f"  - {len(hub_lons)} sân bay Hub")
    if airports_not_found:
        print(f"  - Cảnh báo: Không tìm thấy tọa độ cho {len(airports_not_found)} sân bay (ví dụ: {airports_not_found[:5]})")


# --- 4. Vẽ đồ thị bằng Matplotlib ---
if regular_lons or hub_lons:
    plt.figure(figsize=(15, 10))
    
    # Vẽ SÂN BAY THƯỜNG
    plt.scatter(regular_lons, regular_lats, 
                s=10, alpha=0.6, color='blue', label='Sân bay (Thường)')
    
    # Vẽ SÂN BAY HUB
    plt.scatter(hub_lons, hub_lats, 
                s=50, alpha=1.0, color='red', marker='*', label='Sân bay (Hub)')

    # Tùy chỉnh đồ thị
    plt.title('Bản đồ phân tán các điểm sân bay (Đã tô màu Hub)', fontsize=16)
    plt.xlabel('Kinh độ (Longitude)')
    plt.ylabel('Vĩ độ (Latitude)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    #hiển thị đồ thị
    print("đang hiển thị đồ thị...")
    plt.show()

else:
    print("\nKhông có dữ liệu để vẽ. Chương trình kết thúc.")