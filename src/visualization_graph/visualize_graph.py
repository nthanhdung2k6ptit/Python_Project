import json
import pandas as pd
import os
import plotly.graph_objects as go

import dash
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate

# --- 1. TẢI DỮ LIỆU (LÀM MỘT LẦN KHI KHỞI ĐỘNG) ---

def load_coords_map(csv_path):
    """Đọc file CSV và tạo từ điển tra cứu tọa độ."""
    try:
        df_airports = pd.read_csv(csv_path)
        coords_map = df_airports.set_index('codeiataairport')[
            ['latitudeairport', 'longitudeairport']
        ].to_dict('index')
        print(f"Đã tạo từ điển tra cứu cho {len(coords_map)} sân bay từ file CSV.")
        return coords_map
    except Exception as e:
        print(f"LỖI khi đọc file CSV: {e}")
    return None

def load_graph_data(json_path):
    """Đọc file JSON (nodes và links) của đồ thị."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data_object = json.load(f)
        nodes = data_object.get('nodes')
        links = data_object.get('links')
        print(f"Đã đọc thành công {len(nodes)} nodes và {len(links)} links từ file JSON.")
        return nodes, links
    except Exception as e:
        print(f"LỖI khi đọc file JSON: {e}")
    return None, None

# --- Tải dữ liệu toàn cục (Global Data) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR)) 

CSV_PATH = os.path.join(ROOT_DIR, 'data', 'cleaned', 'airport_db_raw_cleaned.csv')
JSON_PATH = os.path.join(ROOT_DIR, 'data', 'graph', 'flight_network.json')

COORDS_MAP = load_coords_map(CSV_PATH)
NODES_LIST, EDGES_LIST = load_graph_data(JSON_PATH)

# --- Xử lý Node để vẽ ---
plot_lons, plot_lats, plot_text, plot_sizes, plot_colors, plot_iata_codes = [], [], [], [], [], []

if NODES_LIST and COORDS_MAP:
    for node in NODES_LIST:
        iata_code = node.get('id')
        coords = COORDS_MAP.get(iata_code)
        
        if coords:
            plot_iata_codes.append(iata_code) 
            plot_lons.append(coords['longitudeairport'])
            plot_lats.append(coords['latitudeairport'])
            
            if node.get('hub') == 1.0 or node.get('hub') is True:
                plot_text.append(f"<b>{iata_code} (Hub)</b>")
                plot_sizes.append(9)
                plot_colors.append('red')
            else:
                plot_text.append(iata_code)
                plot_sizes.append(4)
                plot_colors.append('blue')

# --- 3. TẠO "LỚP" (TRACE) SÂN BAY CƠ SỞ ---
node_trace = go.Scattergeo(
    lon = plot_lons,
    lat = plot_lats,
    text = plot_text,
    customdata = plot_iata_codes,
    mode = 'markers',
    hoverinfo = 'text',
    marker = dict(
        color = plot_colors,
        size = plot_sizes,
        opacity = 0.8,
        line = dict(width=1, color='rgba(0, 0, 0, 0.5)')
    ),
    name = 'Sân bay'
)

# Layout cơ sở
base_layout = go.Layout(
    title_text = 'Mạng lưới Sân bay (Click vào một điểm)',
    showlegend = True,
    geo = dict(
        scope='world', projection_type='natural earth',
        showland = True, landcolor = 'rgb(243, 243, 243)',
        subunitcolor = 'rgb(217, 217, 217)', countrycolor = 'rgb(217, 217, 217)',
        bgcolor = 'rgba(0,0,0,0)',
    ),
    margin={"r":0,"t":40,"l":0,"b":0}
)
base_fig = go.Figure(data=[node_trace], layout=base_layout)

# --- 4. KHỞI TẠO ỨNG DỤNG DASH ---
app = dash.Dash(__name__)
server = app.server

# --- 5. ĐỊNH NGHĨA BỐ CỤC (LAYOUT) CỦA WEB ---
# *** THAY ĐỔI 1: Thêm Hộp thông tin (Div) ***
app.layout = html.Div([
    html.H1("Trực quan hóa Mạng lưới chuyến bay"),
    html.P("Click vào một sân bay (điểm) trên bản đồ để xem các đường bay của nó."),
    
    dcc.Graph(
        id='flight-map',
        figure=base_fig
    ),
    
    # Hộp thông tin sẽ hiển thị ở đây
    html.Div(
        id='flight-info-box',
        children=[html.P("Hãy click vào một sân bay để xem chi tiết các chuyến bay.")],
        style={
            'padding': '20px',
            'border': '1px solid #ddd',
            'borderRadius': '5px',
            'marginTop': '20px',
            'height': '300px',
            'overflowY': 'scroll', # Cho phép cuộn nếu list quá dài
            'backgroundColor': '#f9f9f9'
        }
    )
])


# --- 6. ĐỊNH NGHĨA PHẦN TƯƠNG TÁC (CALLBACK) ---
# *** THAY ĐỔI 2: Thêm 1 Output cho 'flight-info-box' ***
@app.callback(
    [Output('flight-map', 'figure'),
     Output('flight-info-box', 'children')],
    [Input('flight-map', 'clickData')]
)
def update_map_on_click(clickData):
    
    # Giá trị trả về ban đầu (khi chưa click)
    default_info = [html.P("Hãy click vào một sân bay để xem chi tiết các chuyến bay.")]
    
    if not clickData:
        # *** THAY ĐỔI 3: Phải trả về 2 giá trị ***
        return base_fig, default_info

    point_data = clickData['points'][0]
    
    if 'customdata' not in point_data:
        print("Click trúng đường bay. Bỏ qua.")
        raise PreventUpdate
    
    clicked_iata = point_data['customdata']
    print(f"Người dùng click vào: {clicked_iata}")

    # --- Logic tìm đường bay và THU THẬP THÔNG TIN ---
    
    reg_edge_lons, reg_edge_lats = [], []
    shortest_edge_coords = None
    min_weight = float('inf')
    
    # Danh sách để chứa thông tin chuyến bay (dạng text)
    flight_details = []

    for edge in EDGES_LIST:
        source = str(edge.get('source'))
        target = str(edge.get('target'))
        
        if source == clicked_iata or target == clicked_iata:
            coords_a = COORDS_MAP.get(source)
            coords_b = COORDS_MAP.get(target)
            weight = edge.get('weight')
            
            # --- THU THẬP THÔNG TIN CHUYẾN BAY ---
            airline = edge.get('airline', 'N/A') # N/A nếu bị thiếu
            flight_num = edge.get('flight', 'N/A')
            
            # Xác định chiều bay để hiển thị
            if source == clicked_iata:
                direction = f"{source} → {target}"
            else:
                direction = f"{target} ← {source}"
            
            # Lưu lại chi tiết chuyến bay
            flight_details.append({
                'text': f"✈️ {airline} {flight_num} | {direction}",
                'weight': weight if weight is not None else float('inf')
            })
            
            # --- Xử lý 'weight' cho MAP (như cũ) ---
            if weight is None:
                weight = float('inf')

            if coords_a and coords_b:
                current_lons = [coords_a['longitudeairport'], coords_b['longitudeairport'], None]
                current_lats = [coords_a['latitudeairport'], coords_b['latitudeairport'], None]

                if weight < min_weight:
                    if shortest_edge_coords:
                        reg_edge_lons.extend(shortest_edge_coords[0])
                        reg_edge_lats.extend(shortest_edge_coords[1])
                    
                    min_weight = weight
                    shortest_edge_coords = (current_lons, current_lats)
                
                else:
                    reg_edge_lons.extend(current_lons)
                    reg_edge_lats.extend(current_lats)

    # --- 3. Tạo Figure MỚI (cho bản đồ) ---
    new_fig = go.Figure()
    
    new_fig.add_trace(
        go.Scattergeo(
            lon=reg_edge_lons, lat=reg_edge_lats, mode='lines',
            line=dict(width=0.7, color='orange'),
            hoverinfo='none', name=f'Đường bay của {clicked_iata}'
        )
    )
    
    if shortest_edge_coords:
        new_fig.add_trace(
            go.Scattergeo(
                lon=shortest_edge_coords[0], lat=shortest_edge_coords[1],
                mode='lines', line=dict(width=3, color='#32CD32'),
                hoverinfo='none', name=f'Đường bay trực tiếp ngắn nhất ({min_weight:.0f} km)'
            )
        )
    
    new_fig.add_trace(node_trace) # Luôn vẽ node ở trên cùng
    
    new_fig.update_layout(
        title_text=f"Hiển thị các đường bay của: {clicked_iata}",
        geo=base_layout.geo, showlegend=True, margin=base_layout.margin
    )
    
    # --- 4. Tạo Nội dung MỚI (cho hộp thông tin) ---
    if not flight_details:
        info_content = [html.P(f"Không tìm thấy chi tiết chuyến bay cho {clicked_iata}.")]
    else:
        # Sắp xếp list chuyến bay theo Tên Hãng, rồi đến Số hiệu
        flight_details.sort(key=lambda x: (x['text']))
        
        info_content = [html.H4(f"Chi tiết các chuyến bay từ/đến {clicked_iata}")]
        # Chuyển list text thành list các component html.P
        for detail in flight_details:
            info_content.append(html.P(detail['text']))

    # --- 5. Trả về CẢ HAI giá trị ---
    return new_fig, info_content

# --- 7. CHẠY ỨNG DỤNG ---
if __name__ == '__main__':
    app.run(debug=True, port=8051)