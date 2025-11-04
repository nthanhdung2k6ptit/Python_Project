Phân chia công việc nhóm
THÀNH VIÊN 1 | Phương Anh - API CONNECTION & DATA FETCHING
Nhiệm vụ:
Viết code kết nối API và lấy dữ liệu từ Aviation Edge

(Gợi ý code cần viết)
Tạo class kết nối Aviation Edge API
Viết function lấy dữ liệu airline routes
Viết function lấy dữ liệu flight schedules
Viết function lấy thông tin airports
Xử lý lỗi khi API không hoạt động
Lưu dữ liệu vào file CSV hoặc cache

THÀNH VIÊN 2 | Ngọc Lan - DATA PROCESSING & CLEANING
Nhiệm vụ:
Xử lý và làm sạch dữ liệu từ API

(Gợi ý code cần viết)
Nhận dữ liệu từ Thành viên 1
Chuyển đổi JSON thành DataFrame (pandas)
Loại bỏ dữ liệu trùng lặp
Xử lý missing values
Chuẩn hóa tên airports (IATA codes)
Tạo DataFrame sạch để dùng cho Graph
 
THÀNH VIÊN 3 | Minh Đức - GRAPH BUILDING & ALGORITHMS
Nhiệm vụ: 
Xây dựng đồ thị mạng lưới và các thuật toán

(Gợi ý code cần viết)
Nhận DataFrame từ Thành viên 2
Xây dựng graph bằng NetworkX (nodes = airports, edges = routes)
Viết thuật toán tìm đường bay ngắn nhất (Dijkstra)
Viết code tìm tất cả đường bay giữa 2 điểm
Tính toán Betweenness Centrality (tìm airport hubs)
Tính toán các metrics: density, average degree, diameter

THÀNH VIÊN 4 | Công Hưng - VISUALIZATION (GRAPH NETWORK)
Nhiệm vụ:
Vẽ đồ thị mạng lưới chuyến bay

(Gợi ý code cần viết)
Nhận graph từ Thành viên 3
Vẽ network graph bằng matplotlib
Highlight shortest path trên graph
Vẽ interactive graph bằng plotly
Tô màu airport hubs khác biệt
Export hình ảnh graph

 
THÀNH VIÊN 5 - VISUALIZATION (MAP & UI)
Nhiệm vụ:
Vẽ bản đồ và tạo giao diện người dùng

(Gợi ý code cần viết)
Vẽ routes trên bản đồ thế giới (folium)
Đánh dấu airports trên map
Vẽ đường bay giữa các thành phố
Tạo giao diện chọn thành phố (dropdown menu)
Tạo buttons để chạy phân tích
Hiển thị kết quả lên màn hình

THÀNH VIÊN 6 | Hữu Trung - DATA ANALYSIS & STATISTICS
Nhiệm vụ:
Phân tích dữ liệu và tạo báo cáo thống kê

(Gợi ý code cần viết)
Tính thống kê tổng quan: số airports, số routes
Phân tích airport nào có nhiều chuyến bay nhất
Phân tích airline nào có nhiều routes nhất
Vẽ biểu đồ thống kê (bar chart, pie chart)
Tạo bảng top 10 airports quan trọng nhất
Xuất báo cáo ra file PDF hoặc Excel
 
LUỒNG LÀM VIỆC:
TV1 (Lấy data từ API) 
  ↓
TV2 (Xử lý & làm sạch data)
  ↓
TV3 (Xây graph & thuật toán) Xây dựng mạng lưới đồ thị từ dữ liệu sạch
  build_graph.py – Xây dựng mạng lưới đồ thị từ dữ liệu sạch
Mục đích:
Nhận dữ liệu đã làm sạch (từ TV2).
Tạo đồ thị hàng không (Flight Network) bằng NetworkX.
Lưu graph ra file (.graphml, .csv, .json).
 Công việc cụ thể:
Mục tiêu			Mô tả
Đọc dữ liệu sạch		Từ data/cleaned/routes_clean.csv
Tạo đồ thị NetworkX	nx.from_pandas_edgelist(df, 'origin', 'destination')
Gán thuộc tính node		Ví dụ: thành phố, tên sân bay, quốc gia
Gán trọng số edge		Ví dụ: số lượng chuyến bay giữa 2 sân bay
Lưu file graph		.graphml và .csv trong data/graphs/
↓ ↓
TV4 (Vẽ graph)  ->  TV5 (Vẽ map & UI)  ->  TV6 (Phân tích stats)

 
CÔNG NGHỆ (THƯ VIỆN GỢI Ý) MỖI NGƯỜI DÙNG:
Thành viên	Thư viện chính
TV1	requests, json
TV2	pandas, numpy
TV3	networkx
TV4	matplotlib, plotly
TV5	folium, streamlit hoặc tkinter
TV6	pandas, seaborn, matplotlib
 
Graph_Network_Project/
│
├── README.md                     # Giới thiệu dự án & hướng dẫn chạy
├── requirements.txt              # Các thư viện cần cài đặt (pip install -r requirements.txt)
│
├── data/                         # Thư mục chứa dữ liệu thô & đã xử lý
│   ├── raw/                      # Dữ liệu gốc từ API (TV1)
│   ├── cleaned/                  # Dữ liệu sau khi làm sạch (TV2)
│   ├── graphs/                   # Lưu graph objects hoặc edge list (TV3)
│   ├── reports/                  # Lưu file PDF/Excel thống kê (TV6)
│   └── .gitkeep
│
├── src/                          # Code nguồn chính
│   ├── api_fetch/                #  Thành viên 1 – API Connection
│   │   ├── __init__.py
│   │   ├── aviation_edge_api.py  # Class & functions lấy dữ liệu từ API
│   │   └── test_api_connection.py
│   │
│   ├── data_processing/          #  Thành viên 2 – Làm sạch dữ liệu
│   │   ├── __init__.py
│   │   └── clean_data.py         # Code xử lý missing values, chuẩn hóa tên
│   │
│   ├── graph_building/           #  Thành viên 3 – Tạo đồ thị & thuật toán
│   │   ├── __init__.py
│   │   ├── build_graph.py        # Xây dựng graph từ DataFrame
│   │   ├── algorithms.py         # Dijkstra, Betweenness, metrics
│   │   └── utils_graph.py
│   │
│   ├── visualization_graph/      #  Thành viên 4 – Vẽ Graph Network
│   │   ├── __init__.py
│   │   ├── visualize_graph.py    # Matplotlib, Plotly
│   │   └── export_graph.py       # Lưu ảnh, định dạng đầu ra
│   │
│   ├── visualization_map/        #  Thành viên 5 – Vẽ Map & Giao diện
│   │   ├── __init__.py
│   │   ├── map_routes.py         # Folium vẽ bản đồ, routes
│   │   ├── ui_streamlit.py       # Tạo menu chọn thành phố
│   │   └── ui_helper.py
│   │
│   ├── data_analysis/            #  Thành viên 6 – Phân tích & Thống kê
│   │   ├── __init__.py
│   │   ├── statistics.py         # Tính toán số liệu
│   │   ├── charts.py             # Biểu đồ (bar, pie, top 10)
│   │   └── export_report.py      # Xuất PDF, Excel
│   │
│   └── main.py                   #  Điểm khởi đầu chạy toàn project
│
└── docs/                         # Tài liệu mô tả project, diagram, hướng dẫn
    ├── architecture.png          # Sơ đồ pipeline (TV1→TV6)
    ├── api_doc.md                # Ghi chú về API
    ├── data_flow.md              # Mô tả pipeline dữ liệu`
    └── group_roles.md            # Phân chia công việc nhóm