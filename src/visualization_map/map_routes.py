import folium
import pandas as pd
from pathlib import Path
import os

def draw_flight_map(airports_file=None, routes_file=None, save_path="data/reports/flight_routes_map.html"):
    # project root
    project_root = Path(__file__).resolve().parents[3]

    # đường dẫn tệp mặc định (tương đối với project root)
    if airports_file is None:
        airports_file = project_root / "data" / "cleaned" / "airport_db_cleaned.csv"
    if routes_file is None:
        routes_file = project_root / "data" / "cleaned" / "routes_cleaned.csv"
    save_path = project_root / save_path

    print("Sử dụng data file airports:", airports_file)
    print("Sử dụng data file routes:", routes_file)

    airports = pd.read_csv(airports_file, encoding="utf-8-sig")
    routes = pd.read_csv(routes_file, encoding="utf-8-sig")

    # Normalize column names (strip/ lower if needed)
    airports.columns = [c.strip() for c in airports.columns]
    routes.columns = [c.strip() for c in routes.columns]

    # Try to find IATA / lat / lon columns in airports
    lower_ap = {c.lower(): c for c in airports.columns}
    iata_col = lower_ap.get("codeiataairport") or lower_ap.get("iata") or lower_ap.get("code_iata")
    lat_col = lower_ap.get("latitudeairport") or lower_ap.get("latitude") or lower_ap.get("lat")
    lon_col = lower_ap.get("longitudeairport") or lower_ap.get("longitude") or lower_ap.get("lon") or lower_ap.get("lng")
    if not (iata_col and lat_col and lon_col):
        raise ValueError(f"Airports CSV missing iata/lat/lon columns. Found: {list(airports.columns)}")

    airports_small = airports[[iata_col, lat_col, lon_col]].rename(columns={iata_col: "iata", lat_col: "latitude", lon_col: "longitude"})
    airports_small = airports_small.drop_duplicates(subset=["iata"]).dropna(subset=["iata"])

    # Merge coords into routes using departure/arrival iata columns if present
    if "departureiata" in routes.columns:
        routes = routes.merge(airports_small.rename(columns={"iata":"departureiata","latitude":"dep_lat","longitude":"dep_lon"}), on="departureiata", how="left")
    if "arrivaliata" in routes.columns:
        routes = routes.merge(airports_small.rename(columns={"iata":"arrivaliata","latitude":"arr_lat","longitude":"arr_lon"}), on="arrivaliata", how="left")

    # Fallback: if routes already have dep_lat/dep_lon/arr_lat/arr_lon use them
    # Create map
    m = folium.Map(location=[15.87, 100.99], zoom_start=5, tiles="CartoDB positron")

    # Add airport markers (use columns found earlier)
    for _, row in airports_small.iterrows():
        folium.CircleMarker([row["latitude"], row["longitude"]],
                            radius=3, color="blue", fill=True,
                            popup=str(row["iata"])).add_to(m)

    # Draw routes (skip if coords missing)
    for _, r in routes.iterrows():
        if pd.isna(r.get("dep_lat")) or pd.isna(r.get("arr_lat")):
            continue
        folium.PolyLine([[r["dep_lat"], r["dep_lon"]], [r["arr_lat"], r["arr_lon"]]],
                        color="gray", weight=1.2, opacity=0.7).add_to(m)

    # ensure folder exists and save
    save_path.parent.mkdir(parents=True, exist_ok=True)
    m.save(save_path)
    print(f"✅ Saved map to: {save_path.resolve()}")
    return m
