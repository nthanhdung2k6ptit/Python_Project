import pandas as pd
import folium
from folium import plugins
from folium.plugins import AntPath
import webbrowser
import os
import sys
from functools import lru_cache
import subprocess
from pathlib import Path

try:
    import streamlit as st
    cache_decorator = st.cache_data
except Exception:
    def cache_decorator(ttl=None, **kwargs):
        def _decorator(func):
            return lru_cache(maxsize=1)(func)
        return _decorator

@cache_decorator(ttl=30)
def load_flight_data(csv_path='data/cleaned_vn/flight_tracker_live_vn_cleaned_vn.csv'):
    """Load flights CSV (cached)"""
    try:
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError:
        print(f"Error: Không tìm thấy file {csv_path}")
        return None

@cache_decorator(ttl=3600)
def load_airports_from_csvs(global_path='data/cleaned/airport_db_cleaned.csv',
                            vn_path='data/cleaned_vn/airport_db_cleaned_vn.csv'):
    """Load airports from provided CSVs (cached). Return dict iata -> {lat, lon, name}"""
    parts = []
    if os.path.exists(global_path):
        parts.append(pd.read_csv(global_path, dtype=str))
    if os.path.exists(vn_path):
        parts.append(pd.read_csv(vn_path, dtype=str))
    if not parts:
        return {}

    df = pd.concat(parts, ignore_index=True, sort=False)

    cols = {c.lower(): c for c in df.columns}

    iata_col = None
    for cand in ('iata_code', 'iata', 'iata3', 'iata_code'.lower()):
        if cand in cols:
            iata_col = cols[cand]
            break
    lat_col = None
    for cand in ('latitude', 'lat', 'geography_latitude'):
        if cand in cols:
            lat_col = cols[cand]
            break
    lon_col = None
    for cand in ('longitude', 'lon', 'geography_longitude'):
        if cand in cols:
            lon_col = cols[cand]
            break
    name_col = None
    for cand in ('airport_name', 'name', 'airpt_name'):
        if cand in cols:
            name_col = cols[cand]
            break

    if iata_col is None or lat_col is None or lon_col is None:
        return {}

    df = df[[iata_col, lat_col, lon_col] + ([name_col] if name_col else [])].copy()
    df = df.rename(columns={iata_col: 'iata', lat_col: 'lat', lon_col: 'lon', **({name_col: 'name'} if name_col else {})})
    df['iata'] = df['iata'].astype(str).str.strip().str.upper()
  
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')

    df = df[df['iata'].notna() & df['lat'].notna() & df['lon'].notna()]
    df = df.drop_duplicates(subset=['iata'], keep='first')

    airport_dict = {}
    for r in df.itertuples(index=False):
        iata = getattr(r, 'iata')
        airport_dict[iata] = {
            'lat': float(getattr(r, 'lat')),
            'lon': float(getattr(r, 'lon')),
            'name': str(getattr(r, 'name', iata)) if 'name' in df.columns else iata
        }
    return airport_dict

def get_airport_coordinates():
    """Return dict of airports loaded from CSVs (no fallback to hard-coded list)."""
    global_path = os.path.join('data', 'cleaned', 'airport_db_cleaned.csv')
    vn_path = os.path.join('data', 'cleaned_vn', 'airport_db_cleaned_vn.csv')
    airports = load_airports_from_csvs(global_path, vn_path)
    return airports

def create_flight_map(df):
    
    m = folium.Map(location=[16.0, 106.0], zoom_start=6, tiles='CartoDB positron')
    
    airports = get_airport_coordinates()
    active_flights = df[df['status'] == 'en-route'].copy()
    
    active_airports = set(active_flights['departure_iata_code'].dropna()) | set(active_flights['arrival_iata_code'].dropna())
    
    
    for airport_code in active_airports:
        if airport_code in airports:
            airport = airports[airport_code]
            departures = len(active_flights[active_flights['departure_iata_code'] == airport_code])
            arrivals = len(active_flights[active_flights['arrival_iata_code'] == airport_code])
            
            popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="margin: 0 0 10px 0; color: #2c3e50;">
                    <i class="fa fa-plane"></i> {airport['name']}
                </h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #ecf0f1;">
                        <td style="padding: 5px;"><b>Mã IATA:</b></td>
                        <td style="padding: 5px;">{airport_code}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #ecf0f1;">
                        <td style="padding: 5px;"><b>Chuyến đi:</b></td>
                        <td style="padding: 5px; color: #27ae60;"><b>{departures}</b></td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><b>Chuyến đến:</b></td>
                        <td style="padding: 5px; color: #e74c3c;"><b>{arrivals}</b></td>
                    </tr>
                </table>
            </div>
            """
            
            folium.Marker(
                location=[airport['lat'], airport['lon']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"<b>{airport['name']}</b> ({airport_code})",
                icon=folium.Icon(color='red', icon='plane', prefix='fa')
            ).add_to(m)
    

    for idx, flight in active_flights.iterrows():
        lat = flight['geography_latitude']
        lon = flight['geography_longitude']
        dep_code = flight['departure_iata_code']
        arr_code = flight['arrival_iata_code']
        
        if dep_code in airports and arr_code in airports:
            flight_number = flight['flight_iata_number']
            altitude = flight['geography_altitude']
            speed = flight['speed_horizontal']
            
            plane_popup_html = f"""
            <div style="font-family: Arial; min-width: 250px;">
                <h4 style="margin: 0 0 10px 0; color: #2980b9;">
                    ✈️ Chuyến bay {flight_number}
                </h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #ecf0f1;">
                        <td style="padding: 5px;"><b>Từ:</b></td>
                        <td style="padding: 5px;">{airports[dep_code]['name']} ({dep_code})</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #ecf0f1;">
                        <td style="padding: 5px;"><b>Đến:</b></td>
                        <td style="padding: 5px;">{airports[arr_code]['name']} ({arr_code})</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #ecf0f1;">
                        <td style="padding: 5px;"><b>Độ cao:</b></td>
                        <td style="padding: 5px; color: #16a085;">{altitude:.0f} m</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><b>Tốc độ:</b></td>
                        <td style="padding: 5px; color: #d35400;">{speed:.0f} km/h</td>
                    </tr>
                </table>
            </div>
            """
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(plane_popup_html, max_width=350),
                tooltip=f"<b>{flight_number}</b><br>{airports[dep_code]['name']} → {airports[arr_code]['name']}",
                icon=folium.features.CustomIcon(
                    icon_image='maybay.png',
                    icon_size=(30, 30),
                    icon_anchor=(15, 15),
                )
            ).add_to(m)
            
            dep_coords = [airports[dep_code]['lat'], airports[dep_code]['lon']]
            arr_coords = [airports[arr_code]['lat'], airports[arr_code]['lon']]
            plane_coords = [lat, lon]
            
            AntPath(
                locations=[dep_coords, plane_coords, arr_coords],
                color='red',
                weight=3,
                opacity=0.7,
                delay=400,
                dash_array=[30, 15],
                pulse_color='white',
                tooltip=f"<b>{flight_number}</b><br>{airports[dep_code]['name']} → {airports[arr_code]['name']}"
            ).add_to(m)
    
    plugins.Fullscreen().add_to(m)
    plugins.MiniMap(toggle_display=True).add_to(m)
    
    return m

def main():
    print("=" * 60)
    print("LIVE FLIGHT TRACKER - VIETNAM AIRLINES")

 
    project_root = Path(__file__).resolve().parents[1]
    run_auto_path = project_root / "src" / "api_fetch" / "run_auto.py"
    if run_auto_path.exists():
        print(f"Chạy API fetcher: {run_auto_path}")
        try:
            subprocess.run([sys.executable, str(run_auto_path)], check=False, timeout=120)
            print("Hoàn tất gọi run_auto.py (hoặc đã timeout sau 120s).")
        except subprocess.TimeoutExpired:
            print("run_auto.py vượt quá thời gian cho phép (120s). Tiếp tục pipeline.")
        except Exception as e:
            print(f"Lỗi khi chạy run_auto.py: {e}")
    else:
        print(f"Không tìm thấy run_auto.py tại: {run_auto_path}")


    clean_data_path = project_root / "src" / "data_processing" / "clean_data.py"
    if clean_data_path.exists():
        print(f"Chạy data cleaner: {clean_data_path}")
        try:
            subprocess.run([sys.executable, str(clean_data_path)], check=True)
            print("Hoàn tất chạy clean_data.py.")
        except subprocess.CalledProcessError as e:
            print(f"clean_data.py trả về mã lỗi: {e.returncode}")
        except Exception as e:
            print(f"Lỗi khi chạy clean_data.py: {e}")
    else:
        print(f"Không tìm thấy clean_data.py tại: {clean_data_path}")

    df = load_flight_data()

    if df is None:
        return
    total_flights = len(df)
    en_route = len(df[df['status'] == 'en-route'])
    landed = len(df[df['status'] == 'landed'])

    print(f"Tổng: {total_flights} | Đang bay: {en_route} | Đã hạ cánh: {landed}")

    map_live = create_flight_map(df)
    output_file = 'flight_tracker_live.html'
    map_live.save(output_file)
    print(f"Đã lưu: {output_file}")
    try:
        webbrowser.open('file://' + os.path.realpath(output_file))
    except:
        pass

if __name__ == "__main__":
    main()