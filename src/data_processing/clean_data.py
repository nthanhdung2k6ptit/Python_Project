import os
import re
import pandas as pd

# -------------------- Đường dẫn --------------------
PROJECT_DIR = r"C:\Users\admin\Documents\Graph_Network_Project"
RAW_DIR   = os.path.join(PROJECT_DIR, "data", "raw_vn")
CLEAN_DIR = os.path.join(PROJECT_DIR, "data", "cleaned")
os.makedirs(CLEAN_DIR, exist_ok=True)

FILES = {
    "flight_tracker_raw_vn": "flight_tracker_raw_vn.csv",
    "routes_raw_vn": "routes_raw_vn.csv",
    "realtime_schedules_raw_vn": "realtime_schedules_raw_vn.csv",
    "historical_schedules_raw_vn": "historical_schedules_raw_vn.csv",
    "nearby_airports_raw_vn": "nearby_airports_raw_vn.csv",
    "autocomplete_raw_vn": "autocomplete_raw_vn.csv",
    "airport_db_raw_vn": "airport_db_raw_vn.csv",
    "city_db_raw_vn": "city_db_raw_vn.csv",
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

# -------------------- Clean chung --------------------
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.dropna(axis=1, how="all", inplace=True)
    df.dropna(how="all", inplace=True)
    df.drop_duplicates(inplace=True)

    obj_cols = [
        c for c in df.select_dtypes(include="object").columns
        if ("iata" not in c.lower() and "icao" not in c.lower()
            and "terminal" not in c.lower() and not is_timezone_col(c))
    ]
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

# -------------------- Clean từng bảng --------------------
def clean_routes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"airline_iata": "airline_iata"})
    keep = [c for c in ["departure_iata","arrival_iata","airline_iata"] if c in df.columns]
    if keep: df = df[keep]
    if all(c in df.columns for c in ["departure_iata","arrival_iata"]):
        df = df[df["departure_iata"] != df["arrival_iata"]]
        df = df[~((df["departure_iata"] == "Unknown") & (df["arrival_iata"] == "Unknown"))]
        df = df.drop_duplicates(subset=["departure_iata","arrival_iata","airline_iata"])
    return df

def clean_airport_db(df: pd.DataFrame) -> pd.DataFrame:
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

    for c in ["iata_code", "icao_code", "city_iata", "country_iso2"]:
        if c in df.columns:
            df[c] = df[c].astype("string").str.upper().str.strip()

    if "country_name" in df.columns or "country_iso2" in df.columns:
        df["country"] = df.get("country_name")
        if "country_iso2" in df.columns:
            df["country"] = df["country"].fillna(df["country_iso2"])

    for c in ["country_name", "country_iso2", "phone", "timezone"]:
        if c in df.columns:
            df.drop(columns=c, inplace=True)

    for c in ["latitude", "longitude", "gmt"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "iata_code" in df.columns and df["iata_code"].notna().any():
        df = df.drop_duplicates(subset=["iata_code"])
    elif "icao_code" in df.columns and df["icao_code"].notna().any():
        df = df.drop_duplicates(subset=["icao_code"])
    return df

def clean_schedule(df: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "iata_code": "airport_iata",
        "departure_iata_code": "departure_iata",
        "arrival_iata_code": "arrival_iata",
        "departure_icao_code": "departure_icao_code",
        "arrival_icao_code": "arrival_icao_code",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    if all(c in df.columns for c in ["departure_iata", "arrival_iata"]):
        df = df[~((df["departure_iata"] == "Unknown") & (df["arrival_iata"] == "Unknown"))]

    drop_cols = [
        "arrival_baggage", "arrival_delay", "arrival_gate",
        "departure_gate", "arrival_terminal", "departure_terminal"
    ]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")
    return df

def clean_flight_tracker(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=str.lower)
    for c in ["system_squawk", "speed_is_ground", "speed_vspeed"]:
        if c in df.columns:
            df.drop(columns=c, inplace=True)
    if all(c in df.columns for c in ["departure_iata", "arrival_iata"]):
        df = df[~((df["departure_iata"] == "Unknown") & (df["arrival_iata"] == "Unknown"))]
    return df

def clean_nearby_airports(df: pd.DataFrame) -> pd.DataFrame:
    if "timezone" in df.columns:
        df.drop(columns=["timezone"], inplace=True)
    return df

def clean_city_db(df: pd.DataFrame) -> pd.DataFrame:
    for c in ["timezone", "phone"]:
        if c in df.columns:
            df.drop(columns=c, inplace=True)
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

    if "routes_raw_vn" in datasets:
        datasets["routes_raw_vn"] = clean_routes(datasets["routes_raw_vn"])
    if "airport_db_raw_vn" in datasets:
        datasets["airport_db_raw_vn"] = clean_airport_db(datasets["airport_db_raw_vn"])
    if "flight_tracker_raw_vn" in datasets:
        datasets["flight_tracker_raw_vn"] = clean_flight_tracker(datasets["flight_tracker_raw_vn"])
    if "nearby_airports_raw_vn" in datasets:
        datasets["nearby_airports_raw_vn"] = clean_nearby_airports(datasets["nearby_airports_raw_vn"])
    if "city_db_raw_vn" in datasets:
        datasets["city_db_raw_vn"] = clean_city_db(datasets["city_db_raw_vn"])
    for key in ["realtime_schedules_raw_vn", "historical_schedules_raw_vn"]:
        if key in datasets:
            datasets[key] = clean_schedule(datasets[key])

    for name, df in datasets.items():
        base_name = name.replace("_raw_vn", "")
        out = os.path.join(CLEAN_DIR, f"{base_name}_cleaned_vn.csv")
        df.to_csv(out, index=False, encoding="utf-8-sig")
        print(f"💾 Saved: {out}")

    print("\n✅ Done cleaning all raw datasets.")

if __name__ == "__main__":
    main()
