import os
import sys
import networkx as nx
import json
import plotly.graph_objects as go
import random
import pandas as pd 
import time

# --- 1. IMPORT DASH VÀ CÁC THÀNH PHẦN ---
try:
    import dash
    from dash import dcc, html
    from dash.dependencies import Input, Output, State
except ImportError:
    print("LỖI: Thư viện Dash chưa được cài đặt.")
    print("Hãy chạy: pip install dash")
    sys.exit(1)

# --- 2. THIẾT LẬP ĐƯỜNG DẪN (PATH) ---
print("Đang thiết lập đường dẫn...")
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(SRC_DIR)

if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

# --- 3. IMPORT TỪ CÁC MODULE KHÁC ---
try:
    from graph_building.build_graph import haversine
    print("Import 'haversine' từ 'graph_building.build_graph' thành công.")
except ImportError as e:
    print(f"LỖI IMPORT: {e}")
    sys.exit(1)

# --- 4. TẢI DỮ LIỆU (GỘP 4 FILES) ---
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'graph')
CLEANED_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'cleaned')
CLEANED_DATA_VN_DIR = os.path.join(PROJECT_ROOT, 'data', 'cleaned_vn')
GLOBAL_JSON_PATH = os.path.join(DATA_DIR, 'flight_network.json') 
GLOBAL_ROUTES_CSV = os.path.join(CLEANED_DATA_DIR, 'routes_cleaned.csv')
VN_ROUTES_CSV = os.path.join(CLEANED_DATA_VN_DIR, 'routes_cleaned_vn.csv') 

SOURCE_COL = 'departure_iata'
TARGET_COL = 'arrival_iata'

print(f"Đang tải NÚT (SÂN BAY) từ: {GLOBAL_JSON_PATH}...")
try:
    with open(GLOBAL_JSON_PATH, 'r', encoding='utf-8') as f:
        graph_data = json.load(f)
    
    G_nodes_only = nx.node_link_graph(graph_data, edges="links")
    print(f"Tải thành công Nút: {G_nodes_only.number_of_nodes()} sân bay.")

    G = nx.DiGraph()
    G.add_nodes_from(G_nodes_only.nodes(data=True))
    
    print(f"Đang tải CẠNH (Toàn Thế Giới) từ: {GLOBAL_ROUTES_CSV}...")
    df_global = pd.read_csv(GLOBAL_ROUTES_CSV)
    
    print(f"Đang tải CẠNH (Việt Nam) từ: {VN_ROUTES_CSV}...")
    df_vn = pd.read_csv(VN_ROUTES_CSV)
    
    df_combined = pd.concat([df_global, df_vn])
    df_combined = df_combined.drop_duplicates(subset=[SOURCE_COL, TARGET_COL])
    print(f"Đã gộp và loại bỏ trùng lặp, tổng cộng có {len(df_combined)} đường bay độc nhất.")

    edges_to_add = []
    for index, row in df_combined.iterrows():
        source = row[SOURCE_COL]
        target = row[TARGET_COL]
        if G.has_node(source) and G.has_node(target):
            edges_to_add.append((source, target))
            
    G.add_edges_from(edges_to_add)
    
    print(f"Graph cuối cùng có: {G.number_of_nodes()} nút, {G.number_of_edges()} cạnh.")

except Exception as e:
    print(f"LỖI KHI TẢI DỮ LIỆU: {e}")
    sys.exit(1)

# --- 5. TÍNH TOÁN LAYOUT (ĐÃ XÓA) ---
# Chúng ta không cần tính toán layout NetworkX nữa vì dùng lon/lat

# Chuẩn bị dữ liệu cho Dropdown
print("Đang chuẩn bị danh sách sân bay cho Dropdown...")
AIRPORT_OPTIONS = [
    {
        'label': f"{G.nodes[node].get('name', 'N/A')} ({node})", 
        'value': node
    } 
    for node in G.nodes() 
    # Lọc các nút có đủ thông tin
    if (G.nodes[node].get('name') and 
        G.nodes[node].get('lat') and 
        G.nodes[node].get('lon'))
]
print("Hoàn tất chuẩn bị.")


# --- 6. HÀM VẼ BIỂU ĐỒ (CORE FUNCTION - SỬA DÙNG LON/LAT) ---
def get_random_color():
    """Tạo một màu hex ngẫu nhiên"""
    return f"#{random.randint(0, 0xFFFFFF):06x}"

def create_graph_figure(node_colors_dict={}, highlight_edges=[]):
    """
    Hàm chính để vẽ/cập nhật biểu đồ.
    - SỬ DỤNG LON/LAT THAY VÌ POS_DICT
    """
    
    base_nodes_lon, base_nodes_lat, base_nodes_text = [], [], [] 
    hl_nodes_lon, hl_nodes_lat, hl_nodes_text, hl_nodes_colors = [], [], [], [] 

    # 1. Phân loại các nút (Nodes)
    for node in G.nodes():
        node_data = G.nodes[node]
        # Lấy lon/lat trực tiếp từ node data
        lon, lat = node_data.get('lon'), node_data.get('lat')
        if lon is None or lat is None: 
            continue
            
        text = f"{node_data.get('name', 'N/A')} ({node})"
        
        if node in node_colors_dict:
            hl_nodes_lon.append(lon) # <-- Dùng lon/lat
            hl_nodes_lat.append(lat)
            hl_nodes_text.append(text)
            hl_nodes_colors.append(node_colors_dict[node])
        else:
            base_nodes_lon.append(lon) # <-- Dùng lon/lat
            base_nodes_lat.append(lat)
            base_nodes_text.append(text)
    
    # 2. Xử lý các cạnh (Edges)
    hl_edges_lon, hl_edges_lat = [], []
    for n1, n2 in highlight_edges:
        try:
            # Lấy lon/lat trực tiếp từ node data
            lon1, lat1 = G.nodes[n1]['lon'], G.nodes[n1]['lat']
            lon2, lat2 = G.nodes[n2]['lon'], G.nodes[n2]['lat']
        except KeyError:
            continue
            
        hl_edges_lon.extend([lon1, lon2, None]) # <-- Dùng lon/lat
        hl_edges_lat.extend([lat1, lat2, None])

    # 3. Tạo các lớp (Traces)
    traces = []
    
    traces.append(go.Scatter(
        x=hl_edges_lon, y=hl_edges_lat, # <-- Dùng lon/lat
        mode='lines', line=dict(width=1, color='red'),
        hoverinfo='none', name="Đường bay được chọn"
    ))
    
    traces.append(go.Scatter(
        x=base_nodes_lon, y=base_nodes_lat, text=base_nodes_text, # <-- Dùng lon/lat
        mode='markers', marker=dict(size=3, color='rgba(150, 150, 150, 0.8)'),
        hoverinfo='text', name="Sân bay"
    ))

    traces.append(go.Scatter(
        x=hl_nodes_lon, y=hl_nodes_lat, text=hl_nodes_text, # <-- Dùng lon/lat
        mode='markers', 
        marker=dict(
            size=8, 
            color=hl_nodes_colors, 
            opacity=1.0
        ),
        hoverinfo='text', name="Sân bay được chọn"
    ))
        
    # 4. Tạo Layout
    layout = go.Layout(
        title="Biểu đồ Mạng lưới Chuyến bay Toàn cầu (Vị trí Kinh độ/Vĩ độ)",
        showlegend=False,
        xaxis=dict(visible=False, showgrid=False, zeroline=False),
        yaxis=dict(visible=False, showgrid=False, zeroline=False),
        plot_bgcolor='white', 
        paper_bgcolor='white',
        margin={"r":0,"t":40,"l":0,"b":0},
        uirevision="some-constant-value", 
        hovermode='closest'
    )
    
    return go.Figure(data=traces, layout=layout)


# --- 7. KHỞI TẠO APP DASH ---
app = dash.Dash(__name__)

app.layout = html.Div(style={'fontFamily': 'Arial'}, children=[
    html.H1("Hệ thống Phân tích Mạng lưới Chuyến bay"),
    
    # Khu vực điều khiển
    html.Div(style={'width': '95%', 'margin': 'auto', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px'}, children=[
        html.H3("Chức năng 1: Tìm đường bay ngắn nhất"),
        
        html.Label("Chọn Sân bay đi (Source):"),
        dcc.Dropdown(
            id='dropdown-source',
            options=AIRPORT_OPTIONS,
            placeholder="Gõ tên hoặc mã sân bay"
        ),
        
        html.Label("Chọn Sân bay đến (Target):", style={'marginTop': '10px'}),
        dcc.Dropdown(
            id='dropdown-target',
            options=AIRPORT_OPTIONS,
            placeholder="Gõ tên hoặc mã sân bay"
        ),
        
        html.Button('Tìm đường bay', id='button-find-path', n_clicks=0, style={'marginTop': '10px', 'padding': '10px'}),
        html.Button('Reset Biểu đồ', id='button-reset', n_clicks=0, style={'marginTop': '10px', 'marginLeft': '10px', 'padding': '10px'}),
        
        html.Pre(id='path-output-text', style={'border': '1px solid #eee', 'padding': '5px', 'background': '#f9f9f9'}),
        
        html.H3("Chức năng 2: Xem kết nối (Click hoặc Gõ tìm)"),
        html.P("Click vào một sân bay bất kỳ TRÊN BIỂU ĐỒ, HOẶC gõ tìm sân bay dưới đây:"),
        
        html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
            dcc.Dropdown(
                id='dropdown-click-search', 
                options=AIRPORT_OPTIONS,
                placeholder="Gõ tên hoặc mã sân bay để xem kết nối...",
                style={'flex': '1'} 
            ),
            html.Button('Xem kết nối', id='button-click-search', n_clicks=0, style={'marginLeft': '10px', 'padding': '10px'})
        ]),
        
        html.Pre(id='click-output-text', style={'border': '1px solid #eee', 'padding': '5px', 'background': '#f9f9f9', 'marginTop': '10px'}),
    ]),
    
    # Biểu đồ chính
    html.Div(style={'border': '1px solid black', 'margin': '20px'}, children=[
        dcc.Graph(
            id='map-graph',
            figure=create_graph_figure(highlight_edges=[]), # <-- Không cần POS
            style={'height': '80vh'}
        )
    ])
])


# --- 8. CALLBACK (PHẦN TƯƠNG TÁC LOGIC) ---
@app.callback(
    [Output('map-graph', 'figure'),
     Output('path-output-text', 'children'),
     Output('click-output-text', 'children')],
    [Input('button-find-path', 'n_clicks'),
     Input('map-graph', 'clickData'),
     Input('button-reset', 'n_clicks'),
     Input('button-click-search', 'n_clicks')], 
    [State('dropdown-source', 'value'),
     State('dropdown-target', 'value'),
     State('dropdown-click-search', 'value')] 
)
def update_map(btn_find_path, clickData, btn_reset, btn_click_search, 
               source_node, target_node, click_search_node): 
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, " ", " "
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Xử lý nút RESET
    if triggered_id == 'button-reset':
        return create_graph_figure(node_colors_dict={}, highlight_edges=[]), " ", " "

    # Xử lý logic TÌM ĐƯỜNG BAY
    if triggered_id == 'button-find-path' and source_node and target_node:
        print(f"Đang tìm đường bay từ {source_node} đến {target_node}")
        
        if source_node not in G:
            return dash.no_update, f"Lỗi: Không tìm thấy sân bay đi: {source_node}", " "
        if target_node not in G:
            return dash.no_update, f"Lỗi: Không tìm thấy sân bay đến: {target_node}", " "
            
        try:
            path_nodes = nx.dijkstra_path(G, source=source_node, target=target_node)
            path_edges = list(zip(path_nodes[:-1], path_nodes[1:]))
            
            node_colors = {node: 'red' for node in path_nodes}
            node_colors[source_node] = 'green'
            node_colors[target_node] = 'green'
            
            figure = create_graph_figure(node_colors_dict=node_colors, highlight_edges=path_edges) # <-- Không cần POS
            
            path_text = f"Đường đi: {' -> '.join(path_nodes)}"
            return figure, path_text, " "
            
        except nx.NetworkXNoPath:
            node_colors = {source_node: 'red', target_node: 'red'}
            figure = create_graph_figure(node_colors_dict=node_colors, highlight_edges=[]) # <-- Không cần POS
            return figure, f"Không tìm thấy đường bay nào giữa {source_node} và {target_node}.", " "
        except Exception as e:
            return dash.no_update, f"Lỗi thuật toán: {e}", " "

    # Logic chung cho cả Click và Gõ tìm
    def handle_click_search(node_iata, node_name):
        if node_iata not in G:
            return dash.no_update, " ", f"Lỗi: Sân bay {node_iata} không có trong graph."

        print(f"Đang tìm kết nối cho: {node_iata}")
        successors = list(G.successors(node_iata))
        if not successors:
            return dash.no_update, " ", f"Sân bay {node_name} ({node_iata}) không có đường bay đi."
            
        edges = [(node_iata, succ) for succ in successors]
        
        node_colors = {succ: get_random_color() for succ in successors}
        node_colors[node_iata] = 'green' 
        
        figure = create_graph_figure(node_colors_dict=node_colors, highlight_edges=edges) # <-- Không cần POS
        click_text = f"Đang xem các kết nối từ: {node_name} ({node_iata}) ({len(successors)} đường bay)"
        
        return figure, " ", click_text

    # Xử lý logic CLICK
    if triggered_id == 'map-graph' and clickData:
        try:
            clicked_text = clickData['points'][0]['text']
            node_iata = clicked_text.split('(')[-1].replace(')', '')
            node_name = clicked_text.split(' (')[0]
            
            return handle_click_search(node_iata, node_name)
        except Exception as e:
            return dash.no_update, " ", f"Lỗi khi xử lý click: {e}"

    # Xử lý logic GÕ TÌM
    if triggered_id == 'button-click-search' and click_search_node:
        try:
            node_iata = click_search_node
            node_name = G.nodes[node_iata].get('name', node_iata)
            
            return handle_click_search(node_iata, node_name)
        except Exception as e:
            return dash.no_update, " ", f"Lỗi khi xử lý gõ tìm: {e}"

    return dash.no_update, " ", " "

# --- 9. CHẠY APP ---
if __name__ == '__main__':
    print("Khởi động Dash server...")
    print("Mở trình duyệt và truy cập: http://127.0.0.1:8050/")
    app.run(debug=True)