# Phân chia công việc nhóm

THÀNH VIÊN 1 | Nguyễn Thị Phương Anh - API CONNECTION & DATA FETCHING
Nhiệm vụ:
Viết code kết nối API và lấy dữ liệu từ Aviation Edge

THÀNH VIÊN 2 | Nguyễn Thị Ngọc Lan - DATA PROCESSING & CLEANING
Nhiệm vụ:
Xử lý và làm sạch dữ liệu từ API

THÀNH VIÊN 3 | Đỗ Minh Đức - GRAPH BUILDING & ALGORITHMS
Nhiệm vụ: 
Xây dựng đồ thị mạng lưới và các thuật toán

THÀNH VIÊN 4 | Nguyễn Hữu Trung - DATA ANALYSIS & STATISTICS
Nhiệm vụ:
Phân tích dữ liệu và tạo báo cáo thống kê

THÀNH VIÊN 5 | Vũ Công Duy Hưng - VISUALIZATION (GRAPH NETWORK)
Nhiệm vụ:
Vẽ đồ thị mạng lưới chuyến bay

THÀNH VIÊN 6 - VISUALIZATION (MAP & UI)
Nhiệm vụ:
Vẽ bản đồ và tạo giao diện người dùng

# Luồng làm việc
TV1 (Lấy data từ API) 
  ↓
TV2 (Xử lý & làm sạch data)
  ↓
TV3 (Xây graph & thuật toán) Xây dựng mạng lưới đồ thị từ dữ liệu sạch
↓ ↓
TV4 (Phân tích stats) -> TV5 (Vẽ graph)  ->  TV6 (Vẽ map & UI)

# Cấu trúc Project
Graph_Network_Project/
│
├── README.md                     # Giới thiệu dự án & hướng dẫn chạy
├── requirements.txt              # Các thư viện cần cài đặt (pip install -r requirements.txt)
│
├── data/                         # Thư mục chứa dữ liệu thô & đã xử lý
│   ├── raw/                      # Dữ liệu gốc từ API (TV1)
│   ├── raw_vn/                   # (                      )
│   ├── cleaned/                  # Dữ liệu sau khi làm sạch (TV2)
│   ├── cleaned_vn/               # (                            )
│   ├── graph/                    # Lưu graph objects hoặc edge list (TV3)
│   ├── reports/                  # Lưu file PDF/Excel thống kê (TV4)
│   └── .gitkeep
│
├── src/                          # Code nguồn chính
│   ├── api_fetch/                #  Thành viên 1 – API Connection
│   │   ├── __init__.py
│   │   ├── aviation_edge_api_vn.py  # Class & functions lấy dữ liệu từ API
│   │   └── api_connection_api.py    (                                    )
│   │
│   ├── data_processing/          # Thành viên 2 – Làm sạch dữ liệu
│   │   ├── __init__.py
│   │   └── clean_data.py         # Code xử lý missing values, chuẩn hóa tên
│   │
│   ├── graph_building/           #  Thành viên 3 – Tạo đồ thị & thuật toán
│   │   ├── __init__.py
│   │   ├── build_graph.py        # Xây dựng graph từ DataFrame
│   │   ├── algorithms.py         # Dijkstra, Betweenness, metrics
│   │   └── test_logic.py
│   │
│   ├── data_analysis/            #  Thành viên 4 – Phân tích & Thống kê
│   │   ├── __init__.py
│   │   ├── statistics_1.py       # Tính toán số liệu
│   │   ├── charts.py             # Biểu đồ (bar, pie, top 10)
│   │   └── export_report.py      # Xuất PDF, Excel
│   │ 
│   ├── visualization_graph/      #  Thành viên 5 – Vẽ Graph Network
│   │   ├── __init__.py
│   │   └─── visualize_graph.py   # Matplotlib, Plotly, đồ thị tương tác
│   │
│   │
│   ├── visualization_map/        #  Thành viên 6 – Vẽ Map & Giao diện
│   │   ├── __init__.py
│   │   ├── map_routes.py         # Folium vẽ bản đồ, routes
│   │   ├── ui_streamlit.py       # Tạo menu chọn thành phố
│   │   ├── 3dmap.py              # Trực quan hóa chuyến bay chuyển tiếp bằng map 3D
│   │   └── ui_helper.py
│   │
│   │
│   └── main.py                   # Điểm khởi đầu chạy toàn project
│
└── docs/                         # Tài liệu mô tả project, (hướng dẫn)
    ├── architecture.png          # Sơ đồ pipeline (TV1→TV6)
    ├── api_doc.md                # Ghi chú về API
    ├── data_flow.md              # Mô tả pipeline dữ liệu`
    └── group_roles.md            # Phân chia công việc nhóm