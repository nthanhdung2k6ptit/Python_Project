import os
import re
import pandas as pd

# Đường dẫn dự án
PROJECT_DIR = r"C:\Users\admin\Documents\Graph_Network_Project"
RAW_DIR   = os.path.join(PROJECT_DIR, "data", "raw")
CLEAN_DIR = os.path.join(PROJECT_DIR, "data", "cleaned")
os.makedirs(CLEAN_DIR, exist_ok=True)

FILES = {
    "flight_tracker_raw": "flight_tracker_raw.csv",
    "routes_raw": "routes_raw.csv",
    "realtime_schedules_raw": "realtime_schedules_raw.csv",
    "historical_schedules_raw": "historical_schedules_raw.csv",
    "nearby_airports_raw": "nearby_airports_raw.csv",
    "autocomplete_raw": "autocomplete_raw.csv",
    "airport_db_raw": "airport_db_raw.csv",
    "city_db_raw": "city_db_raw.csv",
}

# -------------------- Utils --------------------
def camel_to_snake(s: str) -> str:
    s = re.sub(r"(?<!^)([A-Z])", r"_\1", s)
    return s.replace("__", "_").lower()

def is_timezone_col(col: str) -> bool:
    c = col.lower()
    return any(k in c for k in ["timezone", "time_zone", "tz", "zone_name"])

def is_datetime_col(col: str) -> bool:
    c = col.lower()
    if any(k in c for k in ["terminal", "iata", "icao", "airport", "city", "country"]):
        return False
    if is_timezone_col(c):
        return False
    keys = ["scheduled", "actual", "updated", "created", "timestamp", "utc", "_time", "time_", "date"]
    return any(k in c for k in keys)

def smart_to_datetime(series: pd.Series) -> pd.Series:
    s = series.copy()
    as_num = pd.to_numeric(s, errors="coerce")
    ratio_num = as_num.notna().mean()
    if ratio_num >= 0.8:
        m = as_num.dropna().abs().median()
        unit = None
        if m > 1e13: unit = "ns"
        elif m > 1e12: unit = "ms"
        elif m > 1e10: unit = "us"
        elif m > 1e9:  unit = "s"
        if unit:
            return pd.to_datetime(as_num, unit=unit, origin="unix", utc=True)
    return pd.to_datetime(s, errors="coerce", utc=True)

def read_csv_safe(path: str) -> pd.DataFrame | None:
    if not os.path.exists(path):
        print(f"⚠️ Missing: {path}")
        return None
    try:
        df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip", low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="ISO-8859-1", on_bad_lines="skip", low_memory=False)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.dropna(how="all", inplace=True)
    return df

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        camel_to_snake(c.strip()).replace(".", "_").replace(" ", "_")
        for c in df.columns
    ]
    return df

# -------------------- Clean: common --------------------
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.dropna(axis=1, how="all", inplace=True)
    df.dropna(how="all", inplace=True)
    df.drop_duplicates(inplace=True)

    # chỉ xử lý object an toàn (không đụng iata/icao/terminal/timezone)
    obj_cols = [
        c for c in df.select_dtypes(include="object").columns
        if ("iata" not in c.lower() and "icao" not in c.lower()
            and "terminal" not in c.lower() and not is_timezone_col(c))
    ]
    for col in obj_cols:
        s = df[col].astype(str).str.strip()
        df[col] = s.replace(["nan","NaN","NULL","None","none","","N/A"], pd.NA)

    # iata/icao upper
    for col in df.columns:
        if "iata" in col or "icao" in col:
            df[col] = df[col].astype("string").str.upper().str.strip()

    # terminal giữ dạng string
    for col in df.columns:
        if col.lower().endswith("terminal"):
            df[col] = df[col].astype("string").str.strip()

    # numeric
    for col in df.columns:
        if any(x in col for x in ["latitude","longitude","lat","lon","speed","altitude","delay","distance"]):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # datetime thông minh
    for col in df.columns:
        if is_datetime_col(col):
            df[col] = smart_to_datetime(df[col])

    # fill Unknown chỉ cho obj_cols an toàn
    if obj_cols:
        df[obj_cols] = df[obj_cols].fillna("Unknown")

    # timezone chỉ strip
    for col in df.columns:
        if is_timezone_col(col) and df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    return df

# -------------------- Clean: per table --------------------
def clean_routes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
        "airline_iata": "airline_iata",
        "departure_iata": "departure_iata",
        "arrival_iata": "arrival_iata",
    })
    keep = [c for c in ["departure_iata","arrival_iata","airline_iata"] if c in df.columns]
    if keep: df = df[keep]
    if all(c in df.columns for c in ["departure_iata","arrival_iata"]):
        df = df.dropna(subset=["departure_iata","arrival_iata"])
        df = df[df["departure_iata"] != df["arrival_iata"]]
        df = df.drop_duplicates(subset=["departure_iata","arrival_iata","airline_iata"])
     # 🔹 Xóa dòng có cả departure & arrival đều Unknown
    if all(c in df.columns for c in ["departure_iata", "arrival_iata"]):
        df = df[~((df["departure_iata"] == "Unknown") & (df["arrival_iata"] == "Unknown"))]

    return df

def clean_airport_db(df: pd.DataFrame) -> pd.DataFrame:
    # 🔹 Chuẩn hoá tên cột (nếu có) theo quy ước thống nhất
    rename = {
        "code_iata_airport": "iata_code",
        "code_icao_airport": "icao_code",
        "name_airport": "airport_name",
        "name_country": "country_name",
        "code_iso2_country": "country_iso2",
        "code_iata_city": "city_iata",
        "latitude_airport": "latitude",
        "longitude_airport": "longitude",
        "gmt": "gmt",
        "geoname_id": "geoname_id",
        "phone": "phone",
        "timezone": "timezone",
        "airport_id": "airport_id",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    # 🔹 Chuẩn hoá các mã định danh
    for c in ["iata_code", "icao_code", "city_iata", "country_iso2"]:
        if c in df.columns:
            df[c] = df[c].astype("string").str.upper().str.strip()

    # 🔹 Tạo 1 cột country duy nhất: ưu tiên country_name, fallback country_iso2
    if "country_name" in df.columns or "country_iso2" in df.columns:
        df["country"] = df.get("country_name")
        if "country_iso2" in df.columns:
            df["country"] = df["country"].fillna(df["country_iso2"])

    # 🔹 Xoá các cột gốc không còn cần thiết
    for c in ["country_name", "country_iso2", "phone"]:
        if c in df.columns:
            df.drop(columns=c, inplace=True)

    # 🔹 Chuyển kiểu dữ liệu toạ độ & GMT
    for c in ["latitude", "longitude"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "gmt" in df.columns:
        df["gmt"] = pd.to_numeric(df["gmt"], errors="coerce")

    # 🔹 Làm sạch timezone (chỉ strip)
    if "timezone" in df.columns and df["timezone"].dtype == object:
        df["timezone"] = df["timezone"].astype(str).str.strip()

    # 🔹 Bỏ trùng theo mã IATA hoặc ICAO
    if "iata_code" in df.columns and df["iata_code"].notna().any():
        df = df.drop_duplicates(subset=["iata_code"])
    elif "icao_code" in df.columns and df["icao_code"].notna().any():
        df = df.drop_duplicates(subset=["icao_code"])
    else:
        df = df.drop_duplicates()

    return df

def clean_schedule(df: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "iata_code": "airport_iata",
        "departure_iata_code": "departure_iata",
        "arrival_iata_code": "arrival_iata",
        "departure_icao_code": "departure_icao_code",
        "arrival_icao_code": "arrival_icao_code",
        "departure_terminal": "departure_terminal",
        "arrival_terminal": "arrival_terminal",
        "departure_scheduled_time_utc": "dep_scheduled_utc",
        "arrival_scheduled_time_utc": "arr_scheduled_utc",
        "departure_actual_time_utc": "dep_actual_utc",
        "arrival_actual_time_utc": "arr_actual_utc",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    need = [c for c in ["departure_iata","arrival_iata"] if c in df.columns]
    if need:
        df = df.dropna(subset=need).drop_duplicates()

    for c in ["departure_terminal","arrival_terminal"]:
        if c in df.columns:
            df[c] = df[c].astype("string").str.strip()
            df.loc[df[c].isin(["nan","None","NULL","Unknown",""]), c] = pd.NA
    if all(c in df.columns for c in ["departure_iata", "arrival_iata"]):
        df = df[~((df["departure_iata"] == "Unknown") & (df["arrival_iata"] == "Unknown"))]
    return df

def clean_flight_tracker(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {}
    for c in df.columns:
        lc = c.lower()
        if "flight_iata" in lc: col_map[c] = "flight_iata"
        elif "flight_icao" in lc: col_map[c] = "flight_icao"
        elif "airline_iata" in lc: col_map[c] = "airline_iata"
        elif "airline_icao" in lc: col_map[c] = "airline_icao"
        elif "departure_iata" in lc or "dep_iata" in lc: col_map[c] = "departure_iata"
        elif "arrival_iata" in lc or "arr_iata" in lc: col_map[c] = "arrival_iata"
        elif "departure_icao" in lc or "dep_icao" in lc: col_map[c] = "departure_icao"
        elif "arrival_icao" in lc or "arr_icao" in lc: col_map[c] = "arrival_icao"
        elif "status" in lc: col_map[c] = "status"
        elif lc.endswith("updated") or "system.updated" in lc: col_map[c] = "system_updated"
    df = df.rename(columns=col_map)
    if all(c in df.columns for c in ["departure_iata","arrival_iata"]):
        df = df.dropna(subset=["departure_iata","arrival_iata"])
    df = df.drop_duplicates()
    if all(c in df.columns for c in ["departure_iata", "arrival_iata"]):
        df = df[~((df["departure_iata"] == "Unknown") & (df["arrival_iata"] == "Unknown"))]

    return df

# -------------------- Pipeline --------------------
def main():
    datasets: dict[str, pd.DataFrame] = {}
    for name, filename in FILES.items():
        path = os.path.join(RAW_DIR, filename)
        df = read_csv_safe(path)
        if df is None:
            continue
        df = normalize_columns(df)
        df = clean_dataframe(df)
        datasets[name] = df
        print(f" Loaded & cleaned: {name} -> {df.shape}")

    if "routes_raw" in datasets:
        datasets["routes_raw"] = clean_routes(datasets["routes_raw"])
    if "airport_db_raw" in datasets:
        datasets["airport_db_raw"] = clean_airport_db(datasets["airport_db_raw"])
    if "flight_tracker_raw" in datasets:
        datasets["flight_tracker_raw"] = clean_flight_tracker(datasets["flight_tracker_raw"])
    for key in ["realtime_schedules_raw", "historical_schedules_raw"]:
        if key in datasets:
            datasets[key] = clean_schedule(datasets[key])
    for name, df in datasets.items():
        base_name = name.replace("_raw", "")  # bỏ hậu tố _raw
        out = os.path.join(CLEAN_DIR, f"{base_name}_cleaned.csv")  # dùng đuôi _cleaned
        df.to_csv(out, index=False, encoding="utf-8-sig")
        print(f"💾 Saved: {out}")


    print("\n Done cleaning all raw datasets.")

if __name__ == "__main__":
    main()
