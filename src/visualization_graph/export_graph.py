import matplotlib.pyplot as plt
import os

def plot_network_map(graph_data, save_path="airport_network_map.png", show_plot=True):
    """
    Vẽ bản đồ mạng lưới sân bay (nodes và edges) bằng Matplotlib.
    
    Args:
        graph_data (dict): Đối tượng dữ liệu đồ thị đã tải từ JSON 
                           (chứa 'nodes' và 'links').
        save_path (str): Tên file để lưu hình ảnh.
        show_plot (bool): Nếu True, sẽ hiển thị đồ thị sau khi chạy.
    """
    
    nodes_list = graph_data.get('nodes', [])
    edges_list = graph_data.get('links', [])
    
    if not nodes_list:
        print("Lỗi: Không tìm thấy 'nodes' trong dữ liệu.")
        return

    # --- 1. Tạo từ điển tra cứu tọa độ (chỉ dùng lon/lat) ---
    # Việc này giúp vẽ các đường bay (edges) nhanh hơn
    coords_map = {}
    for node in nodes_list:
        try:
            # Key 'id' là mã IATA, 'lon' và 'lat' đã có từ file JSON
            coords_map[node['id']] = (node['lon'], node['lat'])
        except KeyError:
            print(f"Cảnh báo: Node {node.get('id')} thiếu thông tin 'lon' hoặc 'lat'.")

    # --- 2. Chuẩn bị dữ liệu Nodes để vẽ (phân loại Hub) ---
    regular_lons, regular_lats = [], []
    hub_lons, hub_lats = [], []

    for node in nodes_list:
        if node.get('id') in coords_map: # Chỉ vẽ node có tọa độ
            lon, lat = coords_map[node['id']]
            
            # Phân loại dựa trên key 'hub' từ JSON
            if node.get('hub') == 1.0 or node.get('hub') is True:
                hub_lons.append(lon)
                hub_lats.append(lat)
            else:
                regular_lons.append(lon)
                regular_lats.append(lat)

    print(f"Đã xử lý: {len(regular_lons)} sân bay thường và {len(hub_lons)} sân bay Hub.")

    # --- 3. Bắt đầu vẽ đồ thị ---
    print("Đang vẽ đồ thị...")
    plt.figure(figsize=(20, 12)) # Kích thước lớn hơn cho chi tiết

    # --- 4. Vẽ các đường bay (Edges) trước ---
    # Vẽ các đường bay (edges) mờ ở lớp dưới cùng
    edge_count = 0
    for edge in edges_list:
        source_id = edge.get('source')
        target_id = edge.get('target')
        
        # Lấy tọa độ điểm đầu và điểm cuối
        source_coords = coords_map.get(str(source_id)) # Chuyển sang str đề phòng
        target_coords = coords_map.get(str(target_id))
        
        if source_coords and target_coords:
            edge_count += 1
            lon_vals = [source_coords[0], target_coords[0]]
            lat_vals = [source_coords[1], target_coords[1]]
            
            # Vẽ đường bay
            plt.plot(lon_vals, lat_vals, 
                     color='gray',   # Màu xám
                     linewidth=0.1,  # Rất mảnh
                     alpha=0.2)       # Rất mờ
    
    print(f"Đã vẽ {edge_count} đường bay.")

    # --- 5. Vẽ các điểm sân bay (Nodes) ---
    # Vẽ SÂN BAY THƯỜNG (lớp trên)
    plt.scatter(regular_lons, regular_lats, 
                s=5, alpha=0.7, color='blue', label='Sân bay (Thường)')
    
    # Vẽ SÂN BAY HUB (lớp trên cùng)
    plt.scatter(hub_lons, hub_lats, 
                s=40, alpha=1.0, color='red', marker='*', label='Sân bay (Hub)')

    # --- 6. Tùy chỉnh và Xuất file ---
    plt.title('Mạng lưới chuyến bay (Nodes và Edges)', fontsize=16)
    plt.xlabel('Kinh độ (Longitude)')
    plt.ylabel('Vĩ độ (Latitude)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Giới hạn trục X và Y để tập trung vào khu vực chính (tùy chọn)
    plt.xlim(-180, 180)
    plt.ylim(-60, 90)

    # Lưu file
    plt.savefig(save_path, dpi=300) # dpi=300 cho ảnh chất lượng cao
    print(f"--- ĐÃ LƯU HÌNH ẢNH ---")
    print(f"Đồ thị đã được lưu thành công vào file: {save_path}")
    
    # Hiển thị đồ thị nếu được yêu cầu
    if show_plot:
        print("--- Đang hiển thị đồ thị... ---")
        plt.show()