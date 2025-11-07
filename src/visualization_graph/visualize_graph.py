import json
import pandas as pd
import os
import plotly.graph_objects as go

# KHÔNG CẦN import 'algorithms' hay 'build_graph'
import dash
from dash import dcc, html, Input, Output
# KHÔNG CẦN 'State' hay 'relayoutData'
from dash.exceptions import PreventUpdate

# --- [ BƯỚC 1: HÀM TẢI DỮ LIỆU ] ---

def load_coords_map(csv_path):
    """Đọc file CSV tọa độ sân bay và tạo từ điển tra cứu."""
    try:
        df_airports = pd.read_csv(csv_path)
        # Dùng cột 'codeiataairport' làm key
        coords_map = df_airports.set_index('codeiataairport')[
            ['latitudeairport', 'longitudeairport']
        ].to_dict('index')
        print(f"Đã tạo từ điển tra cứu cho {len(coords_map)} sân bay từ file CSV.")
        return coords_map
    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file CSV tại: '{csv_path}'")
    except KeyError:
        print(f"LỖI: File CSV tại '{csv_path}' không có cột 'codeiataairport'.")
    except Exception as e:
        print(f"LỖI khi đọc file CSV (airport): {e}")
    return None

def load_graph_data(json_path):
    """Đọc file JSON (nodes và links 'active')."""
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

# --- [ BƯỚC 2: TẢI DỮ LIỆU TOÀN CỤC (GLOBAL) ] ---
# Xác định đường dẫn
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR)) 

# File 1: Tọa độ (Dùng đường dẫn 'cleaned' và tên file đúng)
CSV_PATH_AIRPORTS = os.path.join(ROOT_DIR, 'data', 'cleaned', 'airport_db_raw_cleaned.csv')
COORDS_MAP = load_coords_map(CSV_PATH_AIRPORTS)

# File 2: Sân bay (Nodes) và Chuyến bay (Links)
JSON_PATH = os.path.join(ROOT_DIR, 'data', 'graph', 'flight_network.json')
NODES_LIST, EDGES_LIST = load_graph_data(JSON_PATH) # Chỉ dùng EDGES_LIST từ file này

# --- [ BƯỚC 3: XỬ LÝ NODE ĐỂ VẼ ] ---
plot_lons, plot_lats, plot_text, plot_sizes, plot_colors, plot_iata_codes = [], [], [], [], [], []

# Chỉ chạy nếu cả 2 file được tải thành công
if NODES_LIST and COORDS_MAP:
    for node in NODES_LIST:
        iata_code = node.get('id')
        coords = COORDS_MAP.get(iata_code) # Tra cứu tọa độ
        
        if coords: # Chỉ xử lý nếu sân bay này có tọa độ
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

# --- [ BƯỚC 4: TẠO "LỚP" SÂN BAY VÀ BẢN ĐỒ CƠ SỞ ] ---
node_trace = go.Scattergeo(
    lon = plot_lons,
    lat = plot_lats,
    text = plot_text,
    customdata = plot_iata_codes, # "Giấu" IATA code vào điểm
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


# --- [ BƯỚC 5: KHỞI TẠO DASH VÀ GIAO DIỆN (LAYOUT) ] ---
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Trực quan hóa Mạng lưới chuyến bay"),
    html.P("Click vào một sân bay (điểm) trên bản đồ để xem các đường bay của nó."),
    
    dcc.Graph(
        id='flight-map',
        figure=base_fig
    ),
    
    html.Div(
        id='flight-info-box',
        children=[html.P("Hãy click vào một sân bay để xem chi tiết các chuyến bay.")],
        style={
            'padding': '20px',
            'border': '1px solid #ddd',
            'borderRadius': '5px',
            'marginTop': '20px',
            'height': '300px',
            'overflowY': 'scroll', 
            'backgroundColor': '#f9f9f9',
            'fontFamily': 'Arial, sans-serif'
        }
    )
])


# --- [ BƯỚC 6: ĐỊNH NGHĨA PHẦN TƯƠNG TÁC (CALLBACK) ] ---
# (Phiên bản đơn giản, không có 'State' hay 'relayoutData')
@app.callback(
    [Output('flight-map', 'figure'),
     Output('flight-info-box', 'children')],
    [Input('flight-map', 'clickData')]
)
def update_map_on_click(clickData):
    
    default_info = [html.P("Hãy click vào một sân bay để xem chi tiết các chuyến bay.")]
    
    if not clickData:
        # Khi mới tải trang, trả về bản đồ gốc
        return base_fig, default_info

    # 1. KIỂM TRA CÚ CLICK
    point_data = clickData['points'][0]
    if 'customdata' not in point_data:
        print("Click trúng đường bay. Bỏ qua.")
        raise PreventUpdate
    clicked_iata = point_data['customdata']
    print(f"Người dùng click vào: {clicked_iata}")

    # 2. LOGIC LỌC (Giống hệt phiên bản ổn định của bạn)
    reg_edge_lons, reg_edge_lats = [], []
    shortest_edge_coords = None
    min_weight = float('inf')
    flight_details = [] 
    
    # Chỉ lặp qua EDGES_LIST (từ file JSON)
    for edge in EDGES_LIST:
        source = str(edge.get('source'))
        target = str(edge.get('target'))
        
        if source == clicked_iata or target == clicked_iata:
            coords_a = COORDS_MAP.get(source)
            coords_b = COORDS_MAP.get(target)
            
            # Sửa lỗi 'weight' (có thể là string, None...)
            weight_from_json = edge.get('weight')
            try:
                map_weight = float(weight_from_json)
            except (ValueError, TypeError, OverflowError):
                map_weight = float('inf')
            
            weight_str = f"{map_weight:.0f} km" if map_weight != float('inf') else "N/A km"

            airline = edge.get('airline', 'N/A')
            flight_num = edge.get('flight', 'N/A')

            if source == clicked_iata:
                direction = f"{source} → {target}"
            else:
                direction = f"{target} ← {source}"
            
            flight_details.append({
                'text': f"✈️ {airline} {flight_num} | {direction} ({weight_str})",
                'weight_val': map_weight
            })
            
            if coords_a and coords_b:
                current_lons = [coords_a['longitudeairport'], coords_b['longitudeairport'], None]
                current_lats = [coords_a['latitudeairport'], coords_b['latitudeairport'], None]

                if map_weight < min_weight: 
                    if shortest_edge_coords:
                        reg_edge_lons.extend(shortest_edge_coords[0])
                        reg_edge_lats.extend(shortest_edge_coords[1])
                    min_weight = map_weight
                    shortest_edge_coords = (current_lons, current_lats)
                else:
                    reg_edge_lons.extend(current_lons)
                    reg_edge_lats.extend(current_lats)

    # 3. TẠO BẢN ĐỒ MỚI
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
    new_fig.add_trace(node_trace)
    
    # 4. TẠO HỘP THÔNG TIN MỚI
    if not flight_details:
        info_content = [html.P(f"Không tìm thấy chi tiết chuyến bay cho {clicked_iata}.")]
    else:
        flight_details.sort(key=lambda x: x['weight_val']) 
        info_content = [html.H4(f"Chi tiết các chuyến bay từ/đến {clicked_iata}")]
        for detail in flight_details:
            style = {'fontWeight': 'normal', 'margin': '5px 0'}
            if detail['weight_val'] == min_weight: 
                style['fontWeight'] = 'bold'
                style['color'] = '#2a9d8f'
            info_content.append(html.P(detail['text'], style=style))

    # 5. CẬP NHẬT LAYOUT (Sẽ reset zoom)
    new_fig.update_layout(
        title_text=f"Hiển thị các đường bay của: {clicked_iata}",
        geo=base_layout.geo, # Dùng lại layout geo gốc
        showlegend=True,
        margin=base_layout.margin
    )

    # 6. TRẢ VỀ KẾT QUẢ
    return new_fig, info_content

# --- [ BƯỚC 7: CHẠY ỨNG DỤNG ] ---
if __name__ == '__main__':
    if not COORDS_MAP:
        print(f"\n!!! LỖI TẢI DỮ LIỆU: Không thể tải tọa độ từ: {CSV_PATH_AIRPORTS}")
    elif not NODES_LIST or not EDGES_LIST:
        print(f"\n!!! LỖI TẢI DỮ LIỆU: Không thể tải nodes/links từ: {JSON_PATH}")
    else:
        print("\n--- Tất cả dữ liệu đã được tải thành công. Khởi động server... ---")
        app.run(debug=True, port=8051)