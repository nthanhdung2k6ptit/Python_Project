import pandas as pd
import plotly.graph_objects as go
import os

# --- [ BƯỚC 1: ĐỊNH NGHĨA ĐƯỜNG DẪN FILE ] ---

# TƯ DUY: Chúng ta cần đọc CẢ HAI file.
# File 1: Sân bay thế giới (file cũ)
FILE_PATH_WORLD = os.path.join('data', 'raw', 'airport_db_raw.csv')
# File 2: Sân bay Việt Nam (file bạn vừa gửi)
FILE_PATH_VN = os.path.join('data', 'raw_vn', 'airport_db_raw_vn.csv')

def plot_combined_airport_map(file_world, file_vn):
    """
    Đọc 2 file CSV (thế giới và VN), gộp lại,
    và vẽ tất cả sân bay lên bản đồ.
    """
    df_all_airports = None # Khởi tạo
    
    try:
        # --- [ BƯỚC 2: ĐỌC VÀ GỘP DỮ LIỆU ] ---
        print(f"Đang đọc file 1: {file_world}...")
        df_world = pd.read_csv(file_world)
        print(f"Tìm thấy {len(df_world)} sân bay (thế giới).")

        print(f"Đang đọc file 2: {file_vn}...")
        df_vn = pd.read_csv(file_vn)
        print(f"Tìm thấy {len(df_vn)} sân bay (Việt Nam).")
        
        # Gộp 2 bảng dữ liệu (DataFrame) thành 1
        # ignore_index=True sẽ tạo lại chỉ mục (index) cho bảng mới
        df_all_airports = pd.concat([df_world, df_vn], ignore_index=True)
        print(f"Đã gộp. Tổng cộng có {len(df_all_airports)} sân bay (trước khi lọc).")

        # --- [ BƯỚC 3: XỬ LÝ DỮ LIỆU GỘP ] ---
        
        # 1. Loại bỏ bất kỳ sân bay nào bị thiếu thông tin kinh độ/vĩ độ
        df_all_airports = df_all_airports.dropna(subset=['latitude', 'longitude', 'iata_code'])
        
        # 2. Xóa các sân bay bị trùng lặp (QUAN TRỌNG)
        # (Ví dụ: nếu 'SGN' có trong cả 2 file, chỉ giữ 1)
        # 'keep='first'' nghĩa là giữ lại bản ghi đầu tiên nó thấy
        original_count = len(df_all_airports)
        df_all_airports = df_all_airports.drop_duplicates(subset=['iata_code'], keep='first')
        print(f"Đã xóa {original_count - len(df_all_airports)} sân bay bị trùng lặp.")
        
        # 3. Tạo 'hover_text' (văn bản khi di chuột)
        df_all_airports['hover_text'] = df_all_airports['airport_name'] + " (" + df_all_airports['iata_code'] + ")"
        
        print(f"Sau khi dọn dẹp, còn lại {len(df_all_airports)} sân bay độc nhất. Đang chuẩn bị vẽ...")

    except FileNotFoundError as e:
        print(f"LỖI: Không tìm thấy file. {e}")
        print("Hãy đảm bảo bạn đang chạy file Python này từ thư mục gốc của dự án.")
        return
    except KeyError as e:
        print(f"LỖI: File CSV thiếu cột cần thiết: {e}")
        print("Hãy đảm bảo cả 2 file có các cột 'latitude', 'longitude', 'iata_code', 'airport_name'.")
        return
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return

    # --- [ BƯỚC 4: VẼ BẢN ĐỒ ] ---
    
    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(
            lon = df_all_airports['longitude'], # Dùng cột kinh độ
            lat = df_all_airports['latitude'],  # Dùng cột vĩ độ
            text = df_all_airports['hover_text'], # Dùng cột text đã tạo
            
            mode = 'markers',
            hoverinfo = 'text',
            marker = dict(
                color = 'blue', 
                size = 3,         
                opacity = 0.7     
            ),
            name = 'Sân bay'
        )
    )

    # Tùy chỉnh layout bản đồ
    fig.update_layout(
        title_text = 'Bản đồ các sân bay (Đã gộp Thế giới + Việt Nam)',
        geo = dict(
            scope='world',
            projection_type='natural earth',
            showland = True,
            landcolor = 'rgb(243, 243, 243)',
            bgcolor = 'rgba(0,0,0,0)',
        ),
        margin={"r":0,"t":40,"l":0,"b":0}
    )
    
    # 5. Hiển thị
    print("--- Hoàn tất! Đang mở bản đồ trong trình duyệt... ---")
    fig.show()

# --- [ BƯỚC 5: CHẠY CHƯƠNG TRÌNH ] ---
if __name__ == "__main__":
    # Yêu cầu cài đặt: Mở terminal và chạy 'pip install pandas plotly'
    plot_combined_airport_map(FILE_PATH_WORLD, FILE_PATH_VN)