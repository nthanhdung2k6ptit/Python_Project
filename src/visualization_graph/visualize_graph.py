# --- 1. IMPORT các thư viện ---
import os
import sys
import networkx as nx
import json
import plotly.graph_objects as go
import random
import pandas as pd 
import time
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

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


# --- 5. TÍNH TOÁN LAYOUT (BƯỚC NẶNG NHẤT) ---
print("\n--- ĐANG TÍNH TOÁN LAYOUT (NetworkX) ---")
start_layout_time = time.time()

layout_dir = os.path.join(PROJECT_ROOT, 'data', 'layout')
layout_file = os.path.join(layout_dir, 'graph_layout.json')

os.makedirs(layout_dir, exist_ok=True) 

if os.path.exists(layout_file):
    print(f"Đang tải layout đã tính toán sẵn từ: {layout_file}")
    with open(layout_file, 'r') as f:
        POS = json.load(f)
    print(f"Tải layout có sẵn hoàn tất! (mất {time.time() - start_layout_time:.2f}s)")
else:
    print("Không tìm thấy file layout, đang tính toán layout mới...")
    print("BƯỚC NÀY SẼ MẤT VÀI PHÚT. VUI LÒNG CHỜ...")
    POS = nx.spring_layout(G, seed=42, k=0.15, iterations=50) 
    print(f"Tính toán layout hoàn tất! (mất {time.time() - start_layout_time:.2f}s)")
    
    print(f"Đang lưu layout vào: {layout_file}...")
    try:
        pos_serializable = {key: list(value) for key, value in POS.items()}
        with open(layout_file, 'w') as f:
            json.dump(pos_serializable, f)
        print("Lưu layout thành công. Lần chạy sau sẽ nhanh hơn.")
    except Exception as e:
        print(f"LỖI khi lưu layout: {e}")

# --- 6. TẠO DANH SÁCH SÂN BAY VÀ QUỐC GIA ---
print("Đang chuẩn bị danh sách Sân bay và Quốc gia...")
AIRPORT_OPTIONS = [] 
AIRPORT_COUNTRY_MAP = {} 
COUNTRY_SET = set() 

for node in G.nodes():
    if node in POS: 
        node_name = G.nodes[node].get('name', 'N/A')
        country = G.nodes[node].get('country', 'Unknown')
        
        if country == 'Unknown':
            continue
            
        option = {'label': f"{node_name} ({node})", 'value': node}
        AIRPORT_OPTIONS.append(option)
        AIRPORT_COUNTRY_MAP[node] = country
        COUNTRY_SET.add(country)

COUNTRY_OPTIONS = [{'label': '--- Tất cả Quốc gia ---', 'value': 'ALL'}] + \
                  [{'label': country, 'value': country} for country in sorted(list(COUNTRY_SET))]
print("Hoàn tất chuẩn bị.")


# --- 7. HÀM VẼ BIỂU ĐỒ (CORE FUNCTION) ---
def get_random_color():
    """Tạo một màu hex ngẫu nhiên"""
    return f"#{random.randint(0, 0xFFFFFF):06x}"

def create_graph_figure(graph, pos_dict, node_colors_dict={}, highlight_edges=[]):
    """
    Hàm chính để vẽ/cập nhật biểu đồ.
    - graph: Graph (G) đã được lọc (subgraph)
    - pos_dict: Dict vị trí (POS) đã được lọc
    """
    
    base_nodes_x, base_nodes_y, base_nodes_text = [], [], [] 
    hl_nodes_x, hl_nodes_y, hl_nodes_text, hl_nodes_colors = [], [], [], [] 

    # 1. Phân loại các nút (Nodes)
    for node in graph.nodes():
        if node not in pos_dict:
            continue 
            
        x, y = pos_dict[node]
        
        text = f"{graph.nodes[node].get('name', 'N/A')} ({node})"
        
        if node in node_colors_dict:
            hl_nodes_x.append(x)
            hl_nodes_y.append(y)
            hl_nodes_text.append(text)
            hl_nodes_colors.append(node_colors_dict[node])
        else:
            base_nodes_x.append(x)
            base_nodes_y.append(y)
            base_nodes_text.append(text)
    
    # 2. Xử lý các cạnh (Edges)
    hl_edges_x, hl_edges_y = [], []
    for n1, n2 in highlight_edges:
        try:
            x1, y1 = pos_dict[n1]
            x2, y2 = pos_dict[n2]
        except KeyError:
            continue
            
        hl_edges_x.extend([x1, x2, None])
        hl_edges_y.extend([y1, y2, None])

    # 3. Tạo các lớp (Traces)
    traces = []
    
    traces.append(go.Scatter(
        x=hl_edges_x, y=hl_edges_y,
        mode='lines', line=dict(width=1, color='red'),
        hoverinfo='none', name="Đường bay được chọn"
    ))
    
    traces.append(go.Scatter(
        x=base_nodes_x, y=base_nodes_y, text=base_nodes_text,
        mode='markers', marker=dict(size=3, color='rgba(150, 150, 150, 0.8)'),
        hoverinfo='text', name="Sân bay"
    ))

    traces.append(go.Scatter(
        x=hl_nodes_x, y=hl_nodes_y, text=hl_nodes_text,
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
        title="Biểu đồ Mạng lưới Chuyến bay Toàn cầu (NetworkX Layout)",
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


# --- 8. KHỞI TẠO APP DASH ---
app = dash.Dash(__name__)

app.layout = html.Div(style={'fontFamily': 'Arial'}, children=[
    html.H1("Hệ thống Phân tích Mạng lưới Chuyến bay"),
    
    # Khu vực điều khiển
    html.Div(style={'width': '95%', 'margin': 'auto', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px'}, children=[
        
        #  Thêm Nút Lọc 
        html.H3("Bộ lọc Chính"),
        html.Label("Lọc Graph theo Quốc gia:"),
        html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
            dcc.Dropdown(
                id='dropdown-country-filter', 
                options=COUNTRY_OPTIONS,
                value='ALL', 
                placeholder="Lọc theo quốc gia...",
                style={'flex': '1'},
                clearable=False
            ),
            html.Button('Lọc Quốc gia', id='button-filter-country', n_clicks=0, style={'marginLeft': '10px', 'padding': '10px'}),
            # THÊM NÚT "XÓA LỌC"
            html.Button('Xóa Lọc', id='button-clear-filter', n_clicks=0, style={'marginLeft': '10px', 'padding': '10px', 'backgroundColor': '#ffcccc'})
        ]),
        html.Hr(style={'margin': '20px 0'}),
        
        # NÚT TÌM ĐƯỜNG BAY
        html.H3("Chức năng 1: Tìm đường bay ngắn nhất"),
        
        html.Label("Chọn Sân bay đi:"),
        dcc.Dropdown(
            id='dropdown-source',
            options=AIRPORT_OPTIONS, 
            placeholder="Gõ tên hoặc mã sân bay"
        ),
        
        html.Label("Chọn Sân bay đến:", style={'marginTop': '10px'}),
        dcc.Dropdown(
            id='dropdown-target',
            options=AIRPORT_OPTIONS, 
            placeholder="Gõ tên hoặc mã sân bay"
        ),
        
        html.Button('Tìm đường bay', id='button-find-path', n_clicks=0, style={'marginTop': '10px', 'padding': '10px'}),
        html.Button('Reset Biểu đồ', id='button-reset', n_clicks=0, style={'marginTop': '10px', 'marginLeft': '10px', 'padding': '10px'}),
        
        html.Pre(id='path-output-text', style={'border': '1px solid #eee', 'padding': '5px', 'background': '#f9f9f9'}),
        
        # NÚT XEM KẾT NỐI BẰNG CLICK HOẶC GÕ TÌM
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
            figure=create_graph_figure(G, POS, highlight_edges=[]),
            style={'height': '80vh'}
        )
    ])
])


# --- 9. CALLBACK 1: CẬP NHẬT CÁC DROPDOWN TÌM KIẾM ---
@app.callback(
    [Output('dropdown-source', 'options'),
     Output('dropdown-target', 'options'),
     Output('dropdown-click-search', 'options'),
     Output('dropdown-source', 'value'), 
     Output('dropdown-target', 'value'), 
     Output('dropdown-click-search', 'value')],
    [Input('dropdown-country-filter', 'value'),
     Input('button-clear-filter', 'n_clicks')] 
)
def update_airport_dropdowns(selected_country, n_clear_filter):
    # Xác định xem ai đã kích hoạt
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Nếu bấm nút Xóa Lọc, reset về 'ALL'
    if triggered_id == 'button-clear-filter':
        return AIRPORT_OPTIONS, AIRPORT_OPTIONS, AIRPORT_OPTIONS, None, None, None

    # Nếu chỉ thay đổi dropdown quốc gia
    if selected_country == 'ALL':
        return AIRPORT_OPTIONS, AIRPORT_OPTIONS, AIRPORT_OPTIONS, None, None, None
    
    filtered_options = [
        option for option in AIRPORT_OPTIONS 
        if AIRPORT_COUNTRY_MAP.get(option['value']) == selected_country
    ]
    return filtered_options, filtered_options, filtered_options, None, None, None


# --- 10. CALLBACK 2 (CHÍNH): CẬP NHẬT BIỂU ĐỒ ---
@app.callback(
    [Output('map-graph', 'figure'),
     Output('path-output-text', 'children'),
     Output('click-output-text', 'children')],
    [Input('button-find-path', 'n_clicks'),
     Input('map-graph', 'clickData'),
     Input('button-reset', 'n_clicks'),
     Input('button-click-search', 'n_clicks'),
     Input('button-filter-country', 'n_clicks'),
     Input('button-clear-filter', 'n_clicks')], # <-- THÊM INPUT MỚI
    [State('dropdown-source', 'value'),
     State('dropdown-target', 'value'),
     State('dropdown-click-search', 'value'),
     State('dropdown-country-filter', 'value')] 
)
def update_map(btn_find_path, clickData, btn_reset, btn_click_search, 
               btn_filter_country, btn_clear_filter, # <-- Biến mới
               source_node, target_node, click_search_node, 
               country_filter): 

    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, " ", " "
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    #  LỌC GRAPH TRƯỚC TIÊN ---
    # Nếu bấm nút Xóa Lọc, ép country_filter về 'ALL'
    if triggered_id == 'button-clear-filter':
        active_G = G
        active_POS = POS
    # Ngược lại, lọc bình thường
    elif country_filter == 'ALL':
        active_G = G 
        active_POS = POS 
    else:
        nodes_to_keep = [
            n for n in G.nodes() 
            if n in POS and G.nodes[n].get('country') == country_filter
        ]
        active_G = G.subgraph(nodes_to_keep)
        active_POS = {node: POS[node] for node in nodes_to_keep}


    
    # Xử lý nút RESET hoặc XÓA LỌC
    # Cả hai đều reset biểu đồ về trạng thái (đã lọc)
    if triggered_id == 'button-reset' or triggered_id == 'button-clear-filter':
        # Reset về graph 'ALL'
        return create_graph_figure(G, POS, node_colors_dict={}, highlight_edges=[]), " ", " "

    # Nếu bấm nút LỌC QUỐC GIA
    if triggered_id == 'button-filter-country':
        # Vẽ lại graph (đã được lọc ở trên)
        return create_graph_figure(active_G, active_POS, node_colors_dict={}, highlight_edges=[]), " ", " "

    # Xử lý logic TÌM ĐƯỜNG BAY
    if triggered_id == 'button-find-path' and source_node and target_node:
        print(f"Đang tìm đường bay từ {source_node} đến {target_node} (trong {country_filter})")
        
        if source_node not in active_G:
            return dash.no_update, f"Lỗi: Sân bay đi {source_node} không thuộc quốc gia đã chọn.", " "
        if target_node not in active_G:
            return dash.no_update, f"Lỗi: Sân bay đến {target_node} không thuộc quốc gia đã chọn.", " "
            
        try:
            path_nodes = nx.dijkstra_path(active_G, source=source_node, target=target_node)
            path_edges = list(zip(path_nodes[:-1], path_nodes[1:]))
            
            node_colors = {node: 'red' for node in path_nodes}
            node_colors[source_node] = 'green'
            node_colors[target_node] = 'green'
            
            figure = create_graph_figure(active_G, active_POS, node_colors_dict=node_colors, highlight_edges=path_edges)
            
            path_text = f"ĐdRường đi: {' -> '.join(path_nodes)}"
            return figure, path_text, " "
            
        except nx.NetworkXNoPath:
            node_colors = {source_node: 'red', target_node: 'red'}
            figure = create_graph_figure(active_G, active_POS, node_colors_dict=node_colors, highlight_edges=[])
            return figure, f"Không tìm thấy đường bay nào (trong quốc gia này) giữa {source_node} và {target_node}.", " "
        except Exception as e:
            return dash.no_update, f"Lỗi thuật toán: {e}", " "

    # Logic chung cho cả Click và Gõ tìm
    def handle_click_search(node_iata, node_name):
        if node_iata not in active_G:
            return dash.no_update, " ", f"Lỗi: Sân bay {node_iata} không có trong graph đã lọc."

        print(f"Đang tìm kết nối cho: {node_iata}")
        successors = list(active_G.successors(node_iata))
        if not successors:
            return dash.no_update, " ", f"Sân bay {node_name} ({node_iata}) không có đường bay đi (trong quốc gia này)."
            
        edges = [(node_iata, succ) for succ in successors]
        
        node_colors = {succ: get_random_color() for succ in successors}
        node_colors[node_iata] = 'green' 
        
        figure = create_graph_figure(active_G, active_POS, node_colors_dict=node_colors, highlight_edges=edges)
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

# --- 11. CALLBACK 3 (MỚI): RESET GIÁ TRỊ DROPDOWN QUỐC GIA ---
# (Callback này chỉ chạy khi bấm Xóa Lọc)
@app.callback(
    Output('dropdown-country-filter', 'value'),
    [Input('button-clear-filter', 'n_clicks')]
)
def clear_country_filter_value(n_clicks):
    if n_clicks > 0:
        return 'ALL' # Reset giá trị dropdown về 'ALL'
    return dash.no_update

# --- 12. CHẠY APP ---
if __name__ == '__main__':
    print("Khởi động Dash server...")
    print("Mở trình duyệt và truy cập: http://127.0.0.1:8050/")
    app.run(debug=True)