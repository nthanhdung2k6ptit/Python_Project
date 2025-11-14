import os
import re
import pandas as pd
from pathlib import Path

# ===== Paths =====
PROJECT_DIR = Path(__file__).resolve().parents[2]  # Graph_Network_Project
PROJECT_DIR = str(PROJECT_DIR)

RAW_DIR_VN   = os.path.join(PROJECT_DIR, "data", "raw_vn")
CLEAN_DIR_VN = os.path.join(PROJECT_DIR, "data", "cleaned_vn")
os.makedirs(CLEAN_DIR_VN, exist_ok=True)

RAW_DIR      = os.path.join(PROJECT_DIR, "data", "raw")
CLEAN_DIR    = os.path.join(PROJECT_DIR, "data", "cleaned")
os.makedirs(CLEAN_DIR, exist_ok=True)

FILES_VN = {
    "flight_tracker_raw_vn": "flight_tracker_raw_vn.csv",
    "routes_raw_vn": "routes_raw_vn.csv",
    "realtime_schedules_raw_vn": "realtime_schedules_raw_vn.csv",
    "nearby_airports_raw_vn": "nearby_airports_raw_vn.csv",
    "autocomplete_raw_vn": "autocomplete_raw_vn.csv",
    "airport_db_raw_vn": "airport_db_raw_vn.csv",
    "city_db_raw_vn": "city_db_raw_vn.csv",
    "airline_db_raw_vn": "airline_db_raw_vn.csv",
    "flight_tracker_live_vn": "flight_tracker_live_vn.csv",
    "realtime_schedules_live_vn": "realtime_schedules_live_vn.csv",
}
FILES_GLOBAL = {k.replace("_vn", ""): v.replace("_vn", "") for k, v in FILES_VN.items()}

# ===== Utils =====
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
    return any(k in c for k in ["scheduled","actual","updated","created","timestamp","utc","_time","time_","date"])

def smart_to_datetime(series: pd.Series) -> pd.Series:
    s = series.copy()
    as_num = pd.to_numeric(s, errors="coerce")
    if as_num.notna().mean() >= 0.8:
        m = as_num.dropna().abs().median()
        unit = "ns" if m > 1e13 else "ms" if m > 1e12 else "us" if m > 1e10 else "s" if m > 1e9 else None
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
    df.columns = [camel_to_snake(c.strip()).replace(".", "_").replace(" ", "_") for c in df.columns]
    return df

# ===== Common clean =====
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.dropna(axis=1, how="all", inplace=True)
    df.dropna(how="all", inplace=True)
    df.drop_duplicates(inplace=True)

    obj_cols = [c for c in df.select_dtypes(include="object").columns
                if ("iata" not in c.lower() and "icao" not in c.lower()
                    and "terminal" not in c.lower() and not is_timezone_col(c))]
    for col in obj_cols:
        s = df[col].astype(str).str.strip()
        df[col] = s.replace(["nan","NaN","NULL","None","none","","N/A"], pd.NA)

    for col in df.columns:
        if "iata" in col or "icao" in col:
            df[col] = df[col].astype("string").str.upper().str.strip()

    for col in df.columns:
        if col.lower().endswith("terminal"):
            df[col] = df[col].astype("string").str.strip()

    for col in df.columns:
        if any(x in col for x in ["latitude","longitude","lat","lon","speed","altitude","delay","distance"]):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in df.columns:
        if is_datetime_col(col):
            df[col] = smart_to_datetime(df[col])

    if obj_cols:
        df[obj_cols] = df[obj_cols].fillna("Unknown")

    for col in df.columns:
        if is_timezone_col(col) and df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()
    return df

# ===== Table-specific clean =====
def clean_routes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        cl = col.lower()
        if "iata" in cl or "icao" in cl:
            df[col] = df[col].astype("string").str.upper().str.strip()
    if all(c in df.columns for c in ["departure_iata","arrival_iata"]):
        df = df.loc[~(df["departure_iata"].astype("string") == df["arrival_iata"].astype("string"))]
    return df.drop_duplicates()

def clean_airport_db(df: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "code_iata_airport":"iata_code","code_icao_airport":"icao_code","name_airport":"airport_name",
        "name_country":"country_name","code_iso2_country":"country_iso2","code_iata_city":"city_iata",
        "latitude_airport":"latitude","longitude_airport":"longitude","gmt":"gmt",
        "geoname_id":"geoname_id","phone":"phone","timezone":"timezone","airport_id":"airport_id",
    }
    df = df.rename(columns={k:v for k,v in rename.items() if k in df.columns})

    # Chuẩn hoá mã
    for c in ["iata_code","icao_code","city_iata","country_iso2"]:
        if c in df.columns:
            df[c] = df[c].astype("string").str.upper().str.strip()

    # Tạo cột country (ưu tiên country_name, fallback country_iso2)
    if "country_name" in df.columns or "country_iso2" in df.columns:
        df["country"] = df.get("country_name")
        if "country_iso2" in df.columns:
            df["country"] = df["country"].fillna(df["country_iso2"])

    # ép country = "Vietnam" nếu country_iso2 = "VN"
    if "country_iso2" in df.columns and "country" in df.columns:
        mask_vn = df["country_iso2"].astype(str).str.strip().str.upper().eq("VN")
        df.loc[mask_vn, "country"] = "Vietnam"

    # dọn Unknown/NA thành Vietnam nếu mã VN
    if "country" in df.columns and "country_iso2" in df.columns:
        mask_unknown = df["country"].astype(str).str.strip().str.lower().isin(["unknown", "nan", "none", ""])
        mask_vn = df["country_iso2"].astype(str).str.strip().str.upper().eq("VN")
        df.loc[mask_unknown & mask_vn, "country"] = "Vietnam"

    # Xoá các cột không cần
    for c in ["country_name","country_iso2","phone","timezone"]:
        if c in df.columns:
            df.drop(columns=c, inplace=True)

    # Kiểu dữ liệu số
    for c in ["latitude","longitude","gmt"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # Nếu latitude hoặc longitude bị thiếu → loại bỏ luôn
    if "latitude" in df.columns and "longitude" in df.columns:
        before = len(df)
        df = df.dropna(subset=["latitude", "longitude"])
        after = len(df)
        print(f"Airport DB: removed {before - after} rows because of missing lat/lon")

    # Khử trùng lặp
    if "iata_code" in df.columns and df["iata_code"].notna().any():
        return df.drop_duplicates(subset=["iata_code"])
    if "icao_code" in df.columns and df["icao_code"].notna().any():
        return df.drop_duplicates(subset=["icao_code"])
    return df.drop_duplicates()

def clean_schedule(df: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "iata_code":"airport_iata","departure_iata_code":"departure_iata","arrival_iata_code":"arrival_iata",
        "departure_icao_code":"departure_icao_code","arrival_icao_code":"arrival_icao_code",
    }
    df = df.rename(columns={k:v for k,v in rename.items() if k in df.columns})
    drop_cols = ["arrival_baggage","arrival_delay","arrival_gate","departure_gate","arrival_terminal","departure_terminal"]
    return df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

def clean_flight_tracker(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=str.lower)
    for c in ["system_squawk","speed_is_ground","speed_vspeed"]:  
        if c in df.columns:
            df.drop(columns=c, inplace=True)
    return df

def clean_nearby_airports(df: pd.DataFrame) -> pd.DataFrame:
    if "timezone" in df.columns:
        df.drop(columns=["timezone"], inplace=True)
    return df

def clean_city_db(df: pd.DataFrame) -> pd.DataFrame:
    for c in ["timezone","phone"]:
        if c in df.columns:
            df.drop(columns=c, inplace=True)
    return df

def clean_autocomplete(df: pd.DataFrame) -> pd.DataFrame:
    for c in ["phone","timezone"]:
        if c in df.columns:
            df.drop(columns=c, inplace=True)
    return df

def _normalize_status_values(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Chuẩn hoá giá trị status về snake_case: 'Not Ready' -> 'not_ready'."""
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r"[\s\-]+", "_", regex=True)   # space/hyphen -> underscore
        )
    return df

def clean_airline_db(df: pd.DataFrame, keep_status: set[str]) -> pd.DataFrame:
    """Clean airline_db cho VN / Global tuỳ tập 'keep_status' truyền vào."""
    df = df.copy()
    df = df.rename(columns=str.lower)

    # xoá cột founding nếu có
    if "founding" in df.columns:
        df.drop(columns=["founding"], inplace=True)

    # chuẩn hoá mã viết hoa
    for c in ["code_iata_airline", "code_icao_airline", "code_iso2_country", "codehub", "code_hub"]:
        if c in df.columns:
            df[c] = df[c].astype("string").str.upper().str.strip()

    # xác định cột status & chuẩn hoá giá trị
    status_col = None
    for cand in ["status_airline", "status"]:
        if cand in df.columns:
            status_col = cand
            break

    if status_col:
        df = _normalize_status_values(df, status_col)
        df[status_col] = df[status_col].replace({"notready": "not_ready"})
        df = df[df[status_col].isin(keep_status)]
    else:
        print("⚠️ airline_db: không tìm thấy cột trạng thái (status_airline/status).")

    df = df.drop_duplicates()
    return df


# ===== AUTO CLEAN CHO FLIGHT TRACKER & REALTIME (LIVE) =====
def auto_clean_dataframe(name: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Chỉ auto-clean cho:
      - flight_tracker_* (raw/live)
      - realtime_schedules_* (raw/live)
    """
    df = normalize_columns(df)
    df = clean_dataframe(df)

    base = re.sub(r"_(live|raw)(_vn)?$", "", name)

    if base.startswith("flight_tracker"):
        df = clean_flight_tracker(df)
    elif base.startswith("realtime_schedules"):
        df = clean_schedule(df)

    return df

def clean_and_save_live(name: str, records: list[dict], client):
    """
    Dùng trong vòng lặp LIVE:
      - name: 'flight_tracker_live' hoặc 'realtime_schedules_live'
      - records: list dict từ API
      - client: object có hàm save_to_csv(records, name)

    Return:
      (cleaned_file_name, unknown_file_name_or_None)
    """
    if not records:
        print(f"⚠️ Không có dữ liệu để clean cho {name}")
        return None, None

    df = pd.DataFrame(records)
    df = auto_clean_dataframe(name, df)

    # ---- TÊN FILE CLEAN THEO ĐÚNG YÊU CẦU ----
    cleaned_name = f"{name}_cleaned"            # VD: flight_tracker_live_cleaned
    unknown_name = f"unknow_{name}_cleaned"     # VD: unknow_flight_tracker_live_cleaned

    # Tách status unknown
    base = re.sub(r"_(live|raw)(_vn)?$", "", name)
    unknown_file_written = None

    if base in ("flight_tracker", "realtime_schedules") and "status" in df.columns:
        mask_unknown = (
            df["status"]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("unknown")
        )
        df_unknown = df[mask_unknown]

        if not df_unknown.empty:
            client.save_to_csv(df_unknown.to_dict(orient="records"), unknown_name)
            print(f"Đã lưu {len(df_unknown)} dòng status='unknown' -> {unknown_name}")
            unknown_file_written = unknown_name

        df = df[~mask_unknown]

    # Lưu bản cleaned
    client.save_to_csv(df.to_dict(orient="records"), cleaned_name)
    print(f" Đã clean & lưu file: {cleaned_name}")

    return cleaned_name, unknown_file_written


# ===== Core pipeline for one folder (batch RAW -> CLEANED) =====
def process_folder(files_map, raw_dir, out_dir):
    datasets: dict[str, pd.DataFrame] = {}

    for name, filename in files_map.items():
        path = os.path.join(raw_dir, filename)
        df = read_csv_safe(path)
        if df is None:
            continue
        df = normalize_columns(df)
        df = clean_dataframe(df)
        datasets[name] = df
        print(f" Loaded & cleaned: {path} -> {df.shape}")

    def g(key): return key if key in datasets else None

    for k in [g("routes_raw_vn"), g("routes_raw")]:
        if k: datasets[k] = clean_routes(datasets[k])
    for k in [g("airport_db_raw_vn"), g("airport_db_raw")]:
        if k: datasets[k] = clean_airport_db(datasets[k])
    for k in [g("flight_tracker_raw_vn"), g("flight_tracker_raw")]:
        if k: datasets[k] = clean_flight_tracker(datasets[k])
    for k in [g("nearby_airports_raw_vn"), g("nearby_airports_raw")]:
        if k: datasets[k] = clean_nearby_airports(datasets[k])
    for k in [g("city_db_raw_vn"), g("city_db_raw")]:
        if k: datasets[k] = clean_city_db(datasets[k])
    for k in [g("autocomplete_raw_vn"), g("autocomplete_raw")]:
        if k: datasets[k] = clean_autocomplete(datasets[k])
    for k in [g("realtime_schedules_raw_vn"), g("realtime_schedules_raw")]:
        if k: datasets[k] = clean_schedule(datasets[k])
    for k in [g("airline_db_raw_vn")]:
        if k: datasets[k] = clean_airline_db(datasets[k], keep_status={"active", "not_ready"})
    for k in [g("airline_db_raw")]:
        if k: datasets[k] = clean_airline_db(datasets[k], keep_status={"active"})

    # save + split unknown (cho batch)
    for name, df in datasets.items():
        suffix = "_vn" if name.endswith("_vn") else ""
        base_name = name.replace(f"_raw{suffix}", "")
        cleaned_filename = f"{base_name}_cleaned{suffix}.csv"
        out = os.path.join(out_dir, cleaned_filename)

        stem = os.path.splitext(cleaned_filename)[0]
        if stem.endswith(suffix) and (
            stem.startswith("flight_tracker_cleaned") or stem.startswith("realtime_schedules_cleaned")
        ):
            if "status" in df.columns:
                mask_unknown = df["status"].astype(str).str.strip().str.lower().eq("unknown")
                unk = df.loc[mask_unknown]
                if not unk.empty:
                    unknow_out = os.path.join(out_dir, f"unknow_{cleaned_filename}")
                    unk.to_csv(unknow_out, index=False, encoding="utf-8-sig")
                    print(f" Saved Unknown rows -> {unknow_out} ({len(unk)} rows)")
                    df = df.loc[~mask_unknown].copy()

        df.to_csv(out, index=False, encoding="utf-8-sig")
        print(f" Saved: {out}")

# ===== Main =====
def main():
    process_folder(FILES_VN, RAW_DIR_VN, CLEAN_DIR_VN)   # VN
    process_folder(FILES_GLOBAL, RAW_DIR, CLEAN_DIR)     # Global
    print("\n Done cleaning & splitting unknown for BOTH datasets.")

if __name__ == "__main__":
    main()
