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

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(SRC_DIR)

if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

try:
    from graph_building.build_graph import haversine
    from graph_building.algorithms import shortest_path, shortest_distance, all_paths, graph_metrics
    print("Import 'haversine' và 4 hàm thuật toán thành công.")
except ImportError as e:
    print(f"LỖI IMPORT: {e}")
    sys.exit(1)

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
    
    print("Đang tính toán trọng số (km) cho các cạnh...")
    start_weight_time = time.time()
    for u, v in G.edges():
        try:
            lat1 = G.nodes[u]['lat']; lon1 = G.nodes[u]['lon']
            lat2 = G.nodes[v]['lat']; lon2 = G.nodes[v]['lon']
            distance = haversine(lat1, lon1, lat2, lon2)
            G[u][v]['weight'] = distance
        except (KeyError, TypeError):
            G[u][v]['weight'] = float('inf')
    print(f"Tính trọng số hoàn tất (mất {time.time() - start_weight_time:.2f}s)")

    print(f"Graph cuối cùng có: {G.number_of_nodes()} nút, {G.number_of_edges()} cạnh.")

except Exception as e:
    print(f"LỖI KHI TẢI DỮ LIỆU: {e}")
    sys.exit(1)

print("Đang chuẩn bị danh sách Sân bay và Quốc gia...")
AIRPORT_OPTIONS = [] 
AIRPORT_COUNTRY_MAP = {} 
COUNTRY_SET = set() 
for node in G.nodes():
    node_data = G.nodes[node]
    node_name = node_data.get('name', 'N/A')
    country = node_data.get('country', 'Unknown')
    lat = node_data.get('lat')
    lon = node_data.get('lon')

    if country == 'Unknown' or lat is None or lon is None:
        continue
        
    option = {'label': f"{node_name} ({node})", 'value': node}
    AIRPORT_OPTIONS.append(option)
    AIRPORT_COUNTRY_MAP[node] = country
    COUNTRY_SET.add(country)

COUNTRY_OPTIONS = [{'label': '--- Tất cả Quốc gia ---', 'value': 'ALL'}] + \
                  [{'label': country, 'value': country} for country in sorted(list(COUNTRY_SET))]
print("Hoàn tất chuẩn bị.")

def get_random_color():
    """Tạo một màu hex ngẫu nhiên"""
    return f"#{random.randint(0, 0xFFFFFF):06x}"

def create_graph_figure(graph, node_colors_dict={}, highlight_edges=[]):
    """
    Hàm chính để vẽ/cập nhật biểu đồ (Phiên bản 3D Scattergeo).
    - graph: Graph (G) đã được lọc (subgraph)
    - node_colors_dict: Các nút cần tô màu (từ tìm đường, click)
    - highlight_edges: Các cạnh cần tô màu (từ tìm đường, click)
    """
    
    base_lats, base_lons, base_texts = [], [], []
    hl_lats, hl_lons, hl_texts, hl_colors = [], [], [], []
    
    for node in graph.nodes():
        data = graph.nodes[node]
        lat = data.get('lat')
        lon = data.get('lon')
        
        if lat is None or lon is None: 
            continue 
            
        text = f"{data.get('name', 'N/A')} ({node})"
        
        if node in node_colors_dict:
            hl_lats.append(lat)
            hl_lons.append(lon)
            hl_texts.append(text)
            hl_colors.append(node_colors_dict[node])
        else:
            base_lats.append(lat)
            base_lons.append(lon)
            base_texts.append(text)
            
    edge_lats, edge_lons = [], []
    for n1, n2 in highlight_edges:
        try:
            lat1, lon1 = graph.nodes[n1]['lat'], graph.nodes[n1]['lon']
            lat2, lon2 = graph.nodes[n2]['lat'], graph.nodes[n2]['lon']
            edge_lats.extend([lat1, lat2, None]) 
            edge_lons.extend([lon1, lon2, None])
        except (KeyError, TypeError):
            continue

    
    traces = []
    
    traces.append(go.Scattergeo(
        lat=edge_lats,
        lon=edge_lons,
        mode='lines',
        line=dict(width=1.5, color='red'),
        hoverinfo='none',
        name="Đường bay"
    ))

    traces.append(go.Scattergeo(
        lat=base_lats,
        lon=base_lons,
        text=base_texts,
        mode='markers',
        marker=dict(
            size=3,
            color='rgba(150, 150, 150, 0.8)',
            opacity=0.8
        ),
        hoverinfo='text',
        name="Sân bay"
    ))
    
    traces.append(go.Scattergeo(
        lat=hl_lats,
        lon=hl_lons,
        text=hl_texts,
        mode='markers',
        marker=dict(
            size=6, 
            color=hl_colors,
            opacity=1.0
        ),
        hoverinfo='text',
        name="Sân bay được chọn"
    ))
        
    layout = go.Layout(
        title="Bản đồ Mạng lưới Chuyến bay 3D",
        showlegend=False,
        # 'geo' là cài đặt cho 'Scattergeo'
        geo=dict(
            projection_type='orthographic', # 3D nằm ở đây chứ đâu
            showland=True,
            landcolor='rgb(217, 217, 217)',
            showcountries=True,
            countrycolor='rgb(255, 255, 255)',
            showocean=True,
            oceancolor='rgb(118, 173, 222)',
            bgcolor='rgba(0,0,0,0)'
        ),
        margin={"r":0,"t":40,"l":0,"b":0},
        uirevision="some-constant-value" 
    )
    
    return go.Figure(data=traces, layout=layout)



app = dash.Dash(__name__)

app.layout = html.Div(style={'fontFamily': 'Arial'}, children=[
    html.H1("Hệ thống Phân tích Mạng lưới Chuyến bay"),
    
    html.Div(style={'width': '95%', 'margin': 'auto', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px'}, children=[
        
        html.H3("Bộ lọc Chính & Thống kê"),
        html.Label("Lọc Graph theo Quốc gia:"),
        html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
            dcc.Dropdown(
                id='dropdown-country-filter', 
                options=COUNTRY_OPTIONS,
                value='ALL', 
                style={'flex': '1'},
                clearable=False
            ),
            html.Button('Lọc Quốc gia', id='button-filter-country', n_clicks=0, style={'marginLeft': '10px', 'padding': '10px'}),
            html.Button('Xóa Lọc', id='button-clear-filter', n_clicks=0, style={'marginLeft': '10px', 'padding': '10px', 'backgroundColor': '#ffcccc'})
        ]),
        
        html.Pre(id='metrics-output-text', style={'border': '1px solid #eee', 'padding': '5px', 'background': '#f9f9f9', 'marginTop': '10px'}),
        
        html.Hr(style={'margin': '20px 0'}),
        
        html.H3("Chức năng 1: Tìm đường bay"),
        
        html.Label("Chọn Sân bay đi:"),
        dcc.Dropdown(id='dropdown-source', options=AIRPORT_OPTIONS, placeholder="Gõ tên hoặc mã sân bay"),
        
        html.Label("Chọn Sân bay đến:", style={'marginTop': '10px'}),
        dcc.Dropdown(id='dropdown-target', options=AIRPORT_OPTIONS, placeholder="Gõ tên hoặc mã sân bay"),
        
        html.Div(style={'marginTop': '10px'}, children=[
            dcc.RadioItems(
                id='radio-path-type',
                options=[{'label': ' Tìm theo Ít chặng (Hops)', 'value': 'hops'}, {'label': ' Tìm theo Ít KM', 'value': 'km'}],
                value='hops', labelStyle={'display': 'inline-block', 'margin-right': '20px'}
            )
        ]),
        
        html.Label("Số chặng tối đa (cho 'Tìm tất cả'):", style={'marginTop': '10px'}),
        dcc.Input(id='input-max-hops', type='number', value=4, min=2, max=7, style={'width': '100px', 'marginRight': '10px'}),
        
        html.Button('Tìm 1 đường bay', id='button-find-path', n_clicks=0, style={'marginTop': '10px', 'padding': '10px'}),
        html.Button('Tìm TẤT CẢ đường bay', id='button-find-all-paths', n_clicks=0, style={'marginTop': '10px', 'marginLeft': '10px', 'padding': '10px'}),
        html.Button('Reset Biểu đồ', id='button-reset', n_clicks=0, style={'marginTop': '10px', 'marginLeft': '10px', 'padding': '10px'}),
        
        html.Pre(id='path-output-text', style={'border': '1px solid #eee', 'padding': '5px', 'background': '#f9f9f9'}),
        
        html.Hr(style={'margin': '20px 0'}),

        html.H3("Chức năng 2: Xem kết nối (Click hoặc Gõ tìm)"),
        html.P("Click vào một sân bay bất kỳ TRÊN BIỂU ĐỒ, HOẶC gõ tìm sân bay dưới đây:"),
        html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
            dcc.Dropdown(
                id='dropdown-click-search', options=AIRPORT_OPTIONS, 
                placeholder="Gõ tên hoặc mã sân bay để xem kết nối...", style={'flex': '1'} 
            ),
            html.Button('Xem kết nối', id='button-click-search', n_clicks=0, style={'marginLeft': '10px', 'padding': '10px'})
        ]),
        html.Pre(id='click-output-text', style={'border': '1px solid #eee', 'padding': '5px', 'background': '#f9f9f9', 'marginTop': '10px'}),
    ]),
    
    # Biểu đồ chính
    html.Div(style={'border': '1px solid black', 'margin': '20px'}, children=[
        dcc.Graph(
            id='map-graph',
            figure=create_graph_figure(G, node_colors_dict={}, highlight_edges=[]),
            style={'height': '80vh'}
        )
    ])
])


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
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'button-clear-filter':
        return AIRPORT_OPTIONS, AIRPORT_OPTIONS, AIRPORT_OPTIONS, None, None, None

    if selected_country == 'ALL':
        return AIRPORT_OPTIONS, AIRPORT_OPTIONS, AIRPORT_OPTIONS, None, None, None
    
    filtered_options = [
        option for option in AIRPORT_OPTIONS 
        if AIRPORT_COUNTRY_MAP.get(option['value']) == selected_country
    ]
    return filtered_options, filtered_options, filtered_options, None, None, None


@app.callback(
    [Output('map-graph', 'figure'),
     Output('path-output-text', 'children'),
     Output('click-output-text', 'children'),
     Output('metrics-output-text', 'children')],
    [Input('button-find-path', 'n_clicks'),
     Input('button-find-all-paths', 'n_clicks'),
     Input('map-graph', 'clickData'),
     Input('button-reset', 'n_clicks'),
     Input('button-click-search', 'n_clicks'),
     Input('button-filter-country', 'n_clicks'),
     Input('button-clear-filter', 'n_clicks')],
    [State('dropdown-source', 'value'),
     State('dropdown-target', 'value'),
     State('dropdown-click-search', 'value'),
     State('dropdown-country-filter', 'value'),
     State('radio-path-type', 'value'),
     State('input-max-hops', 'value')]
)
def update_map(btn_find_path, btn_find_all_paths,
               clickData, btn_reset, btn_click_search, 
               btn_filter_country, btn_clear_filter,
               source_node, target_node, click_search_node, 
               country_filter, path_type, 
               max_hops): 

    ctx = dash.callback_context
    triggered_id = 'N/A'
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'button-clear-filter':
        country_filter = 'ALL' 

    if country_filter == 'ALL':
        active_G = G 
    else:
        nodes_to_keep = [
            n for n in G.nodes() 
            if G.nodes[n].get('country') == country_filter
        ]
        active_G = G.subgraph(nodes_to_keep)

    metrics = graph_metrics(active_G)
    metrics_text = (
        f"--- THỐNG KÊ MẠNG LƯỚI ĐANG XEM ---\n"
        f"Quốc gia: {country_filter}\n"
        f"Số sân bay: {active_G.number_of_nodes()}\n"
        f"Số đường bay: {active_G.number_of_edges()}\n"
        f"Mật độ mạng lưới: {metrics['density']:.4f}\n"
        f"Số đường bay TB (mỗi sân bay): {metrics['average_degree']:.2f}"
    )

    if not ctx.triggered:
        return dash.no_update, " ", " ", metrics_text

    if triggered_id == 'button-reset' or triggered_id == 'button-clear-filter':
        return create_graph_figure(G, node_colors_dict={}, highlight_edges=[]), " ", " ", metrics_text

    if triggered_id == 'button-filter-country':
        return create_graph_figure(active_G, node_colors_dict={}, highlight_edges=[]), " ", " ", metrics_text

    if triggered_id == 'button-find-path' and source_node and target_node:
        if source_node not in active_G:
            return dash.no_update, f"Lỗi: Sân bay đi {source_node} không thuộc quốc gia đã chọn.", " ", dash.no_update
        if target_node not in active_G:
            return dash.no_update, f"Lỗi: Sân bay đến {target_node} không thuộc quốc gia đã chọn.", " ", dash.no_update
        try:
            path_nodes = None; path_info_prefix = ""
            if path_type == 'hops':
                path_nodes = shortest_path(active_G, source_node, target_node)
                path_info_prefix = "Đường đi ít chặng nhất (Hops):"
            else: # 'km'
                path_nodes = shortest_distance(active_G, source_node, target_node)
                path_info_prefix = "Đường đi ngắn nhất (KM):"
            if path_nodes is None: raise nx.NetworkXNoPath
            
            path_edges = list(zip(path_nodes[:-1], path_nodes[1:]))
            total_distance = sum(active_G[u][v].get('weight', 0) for u, v in path_edges)
            node_colors = {node: 'red' for node in path_nodes}
            node_colors[source_node] = 'green'; node_colors[target_node] = 'green'
            
            figure = create_graph_figure(active_G, node_colors_dict=node_colors, highlight_edges=path_edges) # (Xóa POS)
            path_text = f"{path_info_prefix} ({len(path_nodes)-1} chặng, {total_distance:.2f} km)\n{' -> '.join(path_nodes)}"
            return figure, path_text, " ", dash.no_update 
            
        except nx.NetworkXNoPath:
            node_colors = {source_node: 'red', target_node: 'red'}
            figure = create_graph_figure(active_G, node_colors_dict=node_colors, highlight_edges=[]) # (Xóa POS)
            return figure, f"Không tìm thấy đường bay nào (loại: {path_type}) giữa {source_node} và {target_node}.", " ", dash.no_update
        except Exception as e:
            return dash.no_update, f"Lỗi thuật toán: {e}", " ", dash.no_update

    if triggered_id == 'button-find-all-paths' and source_node and target_node:
        if max_hops is None or not (2 <= int(max_hops) <= 7):
             return dash.no_update, f"Lỗi: Vui lòng đặt 'Số chặng tối đa' từ 2 đến 7.", " ", dash.no_update
        try:
            paths_list = all_paths(active_G, source_node, target_node, max_hops=int(max_hops))
            if not paths_list:
                node_colors = {source_node: 'red', target_node: 'red'}
                figure = create_graph_figure(active_G, node_colors_dict=node_colors, highlight_edges=[]) # (Xóa POS)
                return figure, f"Không tìm thấy đường bay nào (max {max_hops} chặng) giữa {source_node} và {target_node}.", " ", dash.no_update

            def get_path_distance(path):
                dist = 0
                for i in range(len(path) - 1):
                    dist += active_G[path[i]][path[i+1]].get('weight', 0)
                return dist
            paths_list.sort(key=get_path_distance)
            
            output_text = f"Tìm thấy {len(paths_list)} đường bay (tối đa {max_hops} chặng).\nHiển thị 5 đường ngắn nhất (theo KM):\n"
            for path in paths_list[:5]:
                dist = get_path_distance(path)
                output_text += f"  - ({len(path)-1} chặng, {dist:.2f} km): {' -> '.join(path)}\n"
            
            first_path = paths_list[0]
            path_edges = list(zip(first_path[:-1], first_path[1:]))
            node_colors = {node: 'red' for node in first_path}
            node_colors[source_node] = 'green'; node_colors[target_node] = 'green'
            figure = create_graph_figure(active_G, node_colors_dict=node_colors, highlight_edges=path_edges) # (Xóa POS)
            return figure, output_text, " ", dash.no_update
        except Exception as e:
            return dash.no_update, f"Lỗi: {e}", " ", dash.no_update

    # (Click/Gõ tìm)
    def handle_click_search(node_iata, node_name):
        if node_iata not in active_G:
            return dash.no_update, " ", f"Lỗi: Sân bay {node_iata} không có trong graph đã lọc.", dash.no_update
        successors = list(active_G.successors(node_iata))
        if not successors:
            return dash.no_update, " ", f"Sân bay {node_name} ({node_iata}) không có đường bay đi (trong quốc gia này).", dash.no_update
        edges = [(node_iata, succ) for succ in successors]
        node_colors = {succ: get_random_color() for succ in successors}
        node_colors[node_iata] = 'green' 
        figure = create_graph_figure(active_G, node_colors_dict=node_colors, highlight_edges=edges) # (Xóa POS)
        click_text = f"Đang xem các kết nối từ: {node_name} ({node_iata}) ({len(successors)} đường bay)"
        return figure, " ", click_text, dash.no_update

    if triggered_id == 'map-graph' and clickData:
        try:
            # (cập nhật) Cách lấy IATA từ 'go.Scatterglobe'
            clicked_text = clickData['points'][0]['text']
            node_iata = clicked_text.split('(')[-1].replace(')', '')
            node_name = clicked_text.split(' (')[0]
            return handle_click_search(node_iata, node_name)
        except Exception as e:
            return dash.no_update, " ", f"Lỗi khi xử lý click: {e}", dash.no_update

    if triggered_id == 'button-click-search' and click_search_node:
        try:
            node_iata = click_search_node
            node_name = G.nodes[node_iata].get('name', node_iata)
            return handle_click_search(node_iata, node_name)
        except Exception as e:
            return dash.no_update, " ", f"Lỗi khi xử lý gõ tìm: {e}", dash.no_update

    return dash.no_update, " ", " ", dash.no_update


@app.callback(
    Output('dropdown-country-filter', 'value'),
    [Input('button-clear-filter', 'n_clicks')]
)
def clear_country_filter_value(n_clicks):
    if n_clicks > 0:
        return 'ALL' 
    return dash.no_update

if __name__ == '__main__':
    print("Khởi động Dash server...")
    print("Mở trình duyệt và truy cập: http://127.0.0.1:8050/")
    app.run(debug=True)
    
