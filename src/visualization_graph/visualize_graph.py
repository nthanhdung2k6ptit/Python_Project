import json
import pandas as pd
import os
import plotly.graph_objects as go
import numpy as np

# --- [ BƯỚC 1: IMPORT HÀM TÍNH KM (haversine) ] ---
import sys
# Tự động tìm đường dẫn đến thư mục 'src'
# TƯ DUY: __file__ là file này (visualize_graph.py)
# SCRIPT_DIR là thư mục .../src/visualization_graph
# SRC_DIR là thư mục .../src
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(SRC_DIR) # Thêm thư mục 'src' vào nơi Python tìm kiếm

try:
    # Import chính xác từ module 'graph_building'
    from graph_building.build_graph import haversine
    print("Đã import hàm 'haversine' từ 'graph_building' thành công.")
except ImportError:
    print(f"LỖI: Không tìm thấy 'build_graph.py' trong '{os.path.join(SRC_DIR, 'graph_building')}'")
    haversine = None

# Import thư viện Dash
import dash
from dash import dcc, html, Input, Output, State 
from dash.exceptions import PreventUpdate

# --- [ BƯỚC 2: CÁC HÀM TẢI DỮ LIỆU ] ---

def load_all_airports(file_world, file_vn):
    """
    Đọc 2 file CSV sân bay (Thế giới + VN), gộp lại,
    và tạo từ điển tra cứu tọa độ (COORDS_MAP).
    """
    try:
        print(f"Đang đọc file 1: {file_world}...")
        df_world = pd.read_csv(file_world)
        
        print(f"Đang đọc file 2: {file_vn}...")
        df_vn = pd.read_csv(file_vn)
        
        df_all_airports = pd.concat([df_world, df_vn], ignore_index=True)
        
        # Xử lý dữ liệu gộp
        df_all_airports = df_all_airports.dropna(subset=['latitude', 'longitude', 'iata_code'])
        df_all_airports = df_all_airports.drop_duplicates(subset=['iata_code'], keep='first')
        
        print(f"Đã gộp và xử lý, có {len(df_all_airports)} sân bay độc nhất.")
        
        # Tạo từ điển tra cứu tọa độ
        coords_map = df_all_airports.set_index('iata_code')[
            ['latitude', 'longitude', 'airport_name'] # Lấy cả tên để dùng sau
        ].to_dict('index')
        
        return coords_map
        
    except FileNotFoundError as e:
        print(f"LỖI: Không tìm thấy file sân bay. {e}")
    except KeyError as e:
        print(f"LỖI: File CSV sân bay thiếu cột {e}. Cần 'iata_code', 'latitude', 'longitude'.")
    except Exception as e:
        print(f"LỖI khi đọc file CSV (airport): {e}")
    return None

def load_all_routes(file_world, file_vn):
    """
    Đọc 2 file CSV routes (Thế giới + VN), gộp lại,
    và trả về một DataFrame chứa TẤT CẢ các đường bay hiện hành.
    """
    try:
        print(f"Đang đọc file 3: {file_world}...")
        df_world_routes = pd.read_csv(file_world)
        
        print(f"Đang đọc file 4: {file_vn}...")
        df_vn_routes = pd.read_csv(file_vn)
        
        df_all_routes = pd.concat([df_world_routes, df_vn_routes], ignore_index=True)
        
        # Chỉ giữ các cột cần thiết
        cols_to_keep = ['departure_iata', 'arrival_iata', 'airline_iata', 'flight_number']
        
        # Sửa lại tên cột nếu file VN dùng tên khác (dự phòng)
        if 'departureiata' in df_all_routes.columns:
             df_all_routes = df_all_routes.rename(columns={
                 'departureiata': 'departure_iata',
                 'arrivaliata': 'arrival_iata',
                 'airlineiata': 'airline_iata'
             })
        
        df_all_routes = df_all_routes[cols_to_keep]
        df_all_routes = df_all_routes.dropna(subset=['departure_iata', 'arrival_iata'])
        df_all_routes = df_all_routes.drop_duplicates()
        
        print(f"Đã gộp và xử lý, có {len(df_all_routes)} đường bay/chuyến bay độc nhất.")
        return df_all_routes
        
    except FileNotFoundError as e:
        print(f"LỖI: Không tìm thấy file routes. {e}")
    except KeyError as e:
        print(f"LỖI: File CSV routes thiếu cột {e}.")
    except Exception as e:
        print(f"LỖI khi đọc file CSV (routes): {e}")
    return None

# --- [ BƯỚC 3: TẢI DỮ LIỆU TOÀN CỤC (GLOBAL) ] ---
# TƯ DUY: ROOT_DIR là thư mục 'Graph_Network_Project'
# vì 'SRC_DIR' là '.../src' và chúng ta đi lùi 1 cấp
ROOT_DIR = os.path.dirname(SRC_DIR) 

# File 1 & 2: Sân bay (Đường dẫn khớp với ảnh chụp)
CSV_PATH_AIRPORT_WORLD = os.path.join(ROOT_DIR, 'data', 'cleaned', 'airport_db_cleaned.csv')
CSV_PATH_AIRPORT_VN = os.path.join(ROOT_DIR, 'data', 'cleaned_vn', 'airport_db_cleaned_vn.csv')
COORDS_MAP = load_all_airports(CSV_PATH_AIRPORT_WORLD, CSV_PATH_AIRPORT_VN)

# File 3 & 4: Đường bay (Đường dẫn khớp với ảnh chụp)
CSV_PATH_ROUTES_WORLD = os.path.join(ROOT_DIR, 'data', 'cleaned', 'routes_cleaned.csv')
CSV_PATH_ROUTES_VN = os.path.join(ROOT_DIR, 'data', 'cleaned_vn', 'routes_cleaned_vn.csv')
ROUTES_DF = load_all_routes(CSV_PATH_ROUTES_WORLD, CSV_PATH_ROUTES_VN)


# --- [ BƯỚC 4: XỬ LÝ NODE ĐỂ VẼ ] ---
plot_lons, plot_lats, plot_text, plot_iata_codes = [], [], [], []

if COORDS_MAP:
    for iata_code, data in COORDS_MAP.items():
        if 'latitude' in data and 'longitude' in data:
            plot_iata_codes.append(iata_code) 
            plot_lons.append(data['longitude'])
            plot_lats.append(data['latitude'])
            plot_text.append(f"{data.get('airport_name', 'N/A')} ({iata_code})")
else:
    print("LỖI: Không có dữ liệu tọa độ (COORDS_MAP) để vẽ.")

# --- [ BƯỚC 5: TẠO "LỚP" SÂN BAY VÀ BẢN ĐỒ CƠ SỞ ] ---
node_trace = go.Scattergeo(
    lon = plot_lons,
    lat = plot_lats,
    text = plot_text,
    customdata = plot_iata_codes,
    mode = 'markers',
    hoverinfo = 'text',
    marker = dict(
        color = 'blue', # Tất cả sân bay đều màu xanh
        size = 3,
        opacity = 0.7
    ),
    name = 'Sân bay'
)

base_layout = go.Layout(
    title_text = 'Bản đồ Sân bay (Gộp 4 file) - Click vào một điểm',
    showlegend = True,
    geo = dict(
        scope='world', projection_type='natural earth',
        showland = True, landcolor = 'rgb(243, 243, 243)',
        bgcolor = 'rgba(0,0,0,0)',
    ),
    margin={"r":0,"t":40,"l":0,"b":0}
)
base_fig = go.Figure(data=[node_trace], layout=base_layout)


# --- [ BƯỚC 6: KHỞI TẠO DASH VÀ GIAO DIỆN (LAYOUT) ] ---
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Trực quan hóa Mạng lưới Đường bay (Làm lại)"),
    html.P("Click vào một sân bay (điểm) trên bản đồ để xem các đường bay của nó."),
    
    dcc.Graph(
        id='flight-map',
        figure=base_fig
    ),
    
    html.Div(
        id='flight-info-box',
        children=[html.P("Hãy click vào một sân bay để xem chi tiết các chuyến bay.")],
        style={
            'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px',
            'marginTop': '20px', 'height': '300px', 'overflowY': 'scroll', 
            'backgroundColor': '#f9f9f9', 'fontFamily': 'Arial, sans-serif'
        }
    )
])


# --- [ BƯỚC 7: ĐỊNH NGHĨA CALLBACK (Đã sửa lỗi 'to_dict') ] ---
@app.callback(
    [Output('flight-map', 'figure'),
     Output('flight-info-box', 'children')],
    [Input('flight-map', 'clickData')],
    [State('flight-map', 'relayoutData')]
)
def update_map_on_click(clickData, relayoutData):
    
    default_info = [html.P("Hãy click vào một sân bay để xem chi tiết.")]
    
    if not clickData:
        raise PreventUpdate

    if haversine is None:
        return base_fig, [html.P("LỖI: Không thể tính khoảng cách, hàm 'haversine' chưa được tải.")]
    if ROUTES_DF is None or COORDS_MAP is None:
        return base_fig, [html.P("LỖI: Dữ liệu đường bay hoặc sân bay chưa được tải đầy đủ.")]

    # 1. LẤY SÂN BAY ĐÃ CLICK
    point_data = clickData['points'][0]
    if 'customdata' not in point_data:
        raise PreventUpdate
    clicked_iata = point_data['customdata']
    print(f"Người dùng click vào: {clicked_iata}")

    # 2. LỌC DỮ LIỆU
    # TƯ DUY: Dùng pandas để lọc DataFrame nhanh hơn là lặp
    related_routes_df = ROUTES_DF[
        (ROUTES_DF['departure_iata'] == clicked_iata) | 
        (ROUTES_DF['arrival_iata'] == clicked_iata)
    ].copy() # .copy() để tránh lỗi

    # 3. CHUẨN BỊ CÁC "XÔ" ĐỂ VẼ
    all_routes_lons, all_routes_lats = [], [] # "Xô" chứa TẤT CẢ đường bay (Cam)
    shortest_route_coords = None               # "Xô" chứa đường ngắn nhất (Xanh lá)
    min_weight = float('inf')
    flight_details = [] 

    # 4. LẶP QUA CÁC ĐƯỜNG BAY ĐÃ LỌC
    for row in related_routes_df.itertuples():
        source = str(row.departure_iata)
        target = str(row.arrival_iata)
        
        coords_a = COORDS_MAP.get(source)
        coords_b = COORDS_MAP.get(target)
        
        if coords_a and coords_b:
            # Tính 'weight' (km)
            weight = haversine(coords_a['latitude'], coords_a['longitude'],
                               coords_b['latitude'], coords_b['longitude'])
            
            current_lons = [coords_a['longitude'], coords_b['longitude'], None]
            current_lats = [coords_a['latitude'], coords_b['latitude'], None]
            
            all_routes_lons.extend(current_lons)
            all_routes_lats.extend(current_lats)
            
            airline = str(row.airline_iata) if pd.notna(row.airline_iata) else "N/A"
            flight_num = str(row.flight_number) if pd.notna(row.flight_number) else ""
            
            flight_details.append({
                'text': f"✈️ {airline} {flight_num} | {source} → {target} ({weight:.0f} km)",
                'weight_val': weight
            })
            
            if weight < min_weight:
                min_weight = weight
                shortest_route_coords = (current_lons, current_lats)

    # 5. TẠO BẢN ĐỒ MỚI
    new_fig = go.Figure()
    
    # Lớp 0: TẤT CẢ đường bay (màu cam, mờ)
    new_fig.add_trace(
        go.Scattergeo(
            lon=all_routes_lons, lat=all_routes_lats, mode='lines',
            line=dict(width=0.7, color='orange'),
            hoverinfo='none', name=f'Đường bay của {clicked_iata}'
        )
    )
    
    # Lớp 1: Đường bay NGẮN NHẤT (màu xanh lá, đậm)
    if shortest_route_coords:
        new_fig.add_trace(
            go.Scattergeo(
                lon=shortest_route_coords[0], lat=shortest_route_coords[1],
                mode='lines', line=dict(width=3, color='#32CD32'),
                hoverinfo='none', name=f'Đường bay trực tiếp ngắn nhất ({min_weight:.0f} km)'
            )
        )
    
    # Lớp 2: Sân bay (luôn ở trên cùng)
    new_fig.add_trace(node_trace)
    
    # 6. TẠO HỘP THÔNG TIN MỚI
    if not flight_details:
        info_content = [html.P(f"Không tìm thấy chi tiết đường bay cho {clicked_iata}.")]
    else:
        flight_details.sort(key=lambda x: x['weight_val']) # Sắp xếp theo km
        info_content = [html.H4(f"Chi tiết các đường bay từ/đến {clicked_iata}")]
        for detail in flight_details:
            style = {'fontWeight': 'normal', 'margin': '5px 0'}
            if detail['weight_val'] == min_weight: 
                style['fontWeight'] = 'bold'; style['color'] = '#2a9d8f'
            info_content.append(html.P(detail['text'], style=style))

    # --- [ BƯỚC 7: CẬP NHẬT LAYOUT (ĐÃ SỬA LỖI 'to_dict') ] ---
    
    # 1. Áp dụng layout cơ sở cho figure mới
    new_fig.update_layout(base_layout)
    
    # 2. Cập nhật tiêu đề
    new_fig.update_layout(
        title_text=f"Hiển thị các đường bay của: {clicked_iata}"
    )

    # 3. Áp dụng lại Zoom (nếu có)
    # TƯ DUY: Cập nhật 'new_fig' trực tiếp,
    # thay vì sửa 'base_layout.to_dict()' (gây lỗi)
    try:
        if relayoutData:
            # Dạng 1: Phẳng (ví dụ: {'geo.center.lat': ...})
            if 'geo.center.lat' in relayoutData and relayoutData['geo.center.lat'] is not None:
                new_fig.update_layout(
                    geo_center_lat=relayoutData['geo.center.lat'],
                    geo_center_lon=relayoutData['geo.center.lon']
                )
            if 'geo.projection.scale' in relayoutData and relayoutData['geo.projection.scale'] is not None:
                new_fig.update_layout(
                    geo_projection_scale=relayoutData['geo.projection.scale']
                )
            
            # Dạng 2: Lồng nhau (ví dụ: {'geo': {'center': ...}})
            elif 'geo' in relayoutData:
                if 'center' in relayoutData['geo'] and relayoutData['geo']['center'] is not None:
                    new_fig.update_layout(geo_center=relayoutData['geo']['center'])
                if ('projection' in relayoutData['geo'] and 
                    'scale' in relayoutData['geo']['projection'] and 
                    relayoutData['geo']['projection']['scale'] is not None):
                    new_fig.update_layout(geo_projection_scale=relayoutData['geo']['projection']['scale'])
    except Exception as e:
        print(f"Cảnh báo: Không thể đọc relayoutData. Sẽ reset zoom. Lỗi: {e}")
        pass
    # --- *** KẾT THÚC SỬA LỖI *** ---

    # 8. TRẢ VỀ KẾT QUẢ
    return new_fig, info_content

# --- [ BƯỚC 8: CHẠY ỨNG DỤNG ] ---
if __name__ == '__main__':
    has_error = False
    if not COORDS_MAP:
        print(f"!!! LỖI TẢI DỮ LIỆU: Không thể tải tọa độ sân bay."); has_error = True
    if ROUTES_DF is None or ROUTES_DF.empty:
        print(f"!!! LỖI TẢI DỮ LIỆU: Không thể tải đường bay."); has_error = True
    if haversine is None:
        print("!!! LỖI IMPORT: Không thể import 'haversine' từ 'build_graph.py'"); has_error = True

    if not has_error:
        print("\n--- Tất cả dữ liệu đã được tải thành công. Khởi động server... ---")
        app.run(debug=True, port=8051)
    else:
        print("\n--- Server không thể khởi động do lỗi tải dữ liệu. ---")