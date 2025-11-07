import pandas as pd
import os

# --- Khai báo thư mục và danh sách file ---
DATA_DIR = "data/raw"

FILES = {
    "flights_raw": "flights_raw.csv",
    "realtime_schedules_raw": "realtime_schedules_raw.csv",
    "historical_schedules_raw": "historical_schedules_raw.csv",
    "future_schedules_raw": "future_schedules_raw.csv",
    "routes_raw": "routes_raw.csv",
    "nearby_airports_raw": "nearby_airports_raw.csv",
    "autocomplete_raw": "autocomplete_raw.csv",
    "satellite_raw": "satellite_raw.csv",
    "airline_db_raw": "airline_db_raw.csv",
    "airport_db_raw": "airport_db_raw.csv"
}

# --- Hàm đọc file an toàn ---
def read_csv_safe(file_path):
    try:
        df = pd.read_csv(file_path, encoding="utf-8", sep=",")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="ISO-8859-1", sep=",")
    except Exception as e:
        print(f"Lỗi khi đọc {file_path}: {e}")
        return None

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.dropna(how='all', inplace=True)
    return df

# --- Đọc toàn bộ file ---
datasets = {}
for name, filename in FILES.items():
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        print(f"Đang đọc file: {filename} ...")
        df = read_csv_safe(path)
        if df is not None:
            datasets[name] = df
            print(f"Đã nạp {name}: {df.shape[0]} dòng, {df.shape[1]} cột\n")
        else:
            print(f"Không thể đọc được nội dung trong {filename}\n")
    else:
        print(f"Không tìm thấy file {filename}\n")

# --- Hàm chuẩn hóa tên cột ---
def normalize_columns(df):
    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_", regex=False)
        .str.replace(".", "_", regex=False)
    )
    return df

# --- Áp dụng chuẩn hóa ---
for name in datasets:
    datasets[name] = normalize_columns(datasets[name])

# --- In thông tin sau khi chuẩn hóa ---
print("Danh sách dataset đã nạp:", list(datasets.keys()))

for name, df in datasets.items():
    print(f"--- {name.upper()} ---")
    print(df.head(3))
    print(df.info())
    print("=" * 70)

# --- Lưu dữ liệu sạch ---
os.makedirs("data/cleaned", exist_ok=True)

for name, df in datasets.items():
    output_path = f"data/cleaned/{name}_cleaned.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Đã lưu: {output_path} ({df.shape[0]} dòng, {df.shape[1]} cột)")
