#1. File 1 | Các cột Dũng sử dụng: iata_code, latitude, longitude, airport_name, country (optional), city_iata (optional)

#2. File 2 | Các cột Dũng sử dụng: departure_iata, arrival_iata, flight_number (popup), airline_iata

import pandas as pd
import folium
from folium.plugins import AntPath
import os
from typing import Optional, Iterable

def create_flight_map(
    base_path = "data/cleaned",
    output_path = "data/reports/flight_routes_map.html",
    departure_filter = None, #IATA
    departure_city_iatas = None,
    allowed_iatas = None
):
    # build file paths (robust with fallbacks)
    airport_global = os.path.join(base_path, "airport_db_cleaned.csv")
    routes_global = os.path.join(base_path, "routes_cleaned.csv")

    # possible VN locations (your repo has data/cleaned_vn/)
    candidates_air_vn = [
        os.path.join(base_path + "_vn", "airport_db_cleaned_vn.csv"),        # data/cleaned_vn/...
        os.path.join(base_path, "vn", "airport_db_cleaned_vn.csv"),         # data/cleaned/vn/...
        os.path.join(os.path.dirname(base_path), "cleaned_vn", "airport_db_cleaned_vn.csv"),  # data/cleaned_vn
        os.path.join("data", "cleaned_vn", "airport_db_cleaned_vn.csv"),
    ]
    candidates_routes_vn = [
        os.path.join(base_path + "_vn", "routes_cleaned_vn.csv"),
        os.path.join(base_path, "vn", "routes_cleaned_vn.csv"),
        os.path.join(os.path.dirname(base_path), "cleaned_vn", "routes_cleaned_vn.csv"),
        os.path.join("data", "cleaned_vn", "routes_cleaned_vn.csv"),
    ]

    # read global files (raise if missing)
    df_air_global = pd.read_csv(airport_global)
    df_route_global = pd.read_csv(routes_global)

    # find and read VN files if exist, otherwise use empty DataFrame
    airport_vn = next((p for p in candidates_air_vn if os.path.exists(p)), None)
    routes_vn = next((p for p in candidates_routes_vn if os.path.exists(p)), None)

    if airport_vn:
        df_air_vn = pd.read_csv(airport_vn)
        # Ignore the 'country' column values coming from the VN file (they contain "Unknown").
        # Use a consistent marker instead so popup won't show "Unknown".
        df_air_vn['country'] = 'Vietnam'
        # mark source (optional, useful later)
        df_air_vn['__src'] = 'vn'
    else:
        # empty DataFrame with same columns as global (if available) to avoid KeyErrors later
        if not df_air_global.empty:
            df_air_vn = pd.DataFrame(columns=df_air_global.columns.tolist() + ['__src'])
        else:
            df_air_vn = pd.DataFrame()

    if routes_vn:
        df_route_vn = pd.read_csv(routes_vn)
        df_route_vn['__src'] = 'vn'
    else:
        if not df_route_global.empty:
            df_route_vn = pd.DataFrame(columns=df_route_global.columns.tolist() + ['__src'])
        else:
            df_route_vn = pd.DataFrame()
    
    # Gộp data toàn cầu và Việt Nam lại, loại bỏ trùng IATA nếu có
    airports = pd.concat([df_air_global, df_air_vn]).drop_duplicates(subset=['iata_code'])
    routes = pd.concat([df_route_global, df_route_vn]).drop_duplicates(subset=['departure_iata', 'arrival_iata'])

    # --- NORMALIZE IATA COLUMNS (uppercase + strip) ---
    if 'iata_code' in airports.columns:
        airports['iata_code'] = airports['iata_code'].astype(str).str.upper().str.strip()
    if 'departure_iata' in routes.columns:
        routes['departure_iata'] = routes['departure_iata'].astype(str).str.upper().str.strip()
    if 'arrival_iata' in routes.columns:
        routes['arrival_iata'] = routes['arrival_iata'].astype(str).str.upper().str.strip()

    # --- If allowed_iatas provided, filter airports and routes early to save memory/time ---
    if allowed_iatas is not None:
        allowed_set = {s.upper().strip() for s in allowed_iatas if isinstance(s, str) and s.strip()}
        # keep only airports in allowed set
        if 'iata_code' in airports.columns:
            airports = airports[airports['iata_code'].isin(allowed_set)].copy()
        # keep only routes where at least one endpoint is in allowed_set
        if not routes.empty:
            routes = routes[
                (routes['departure_iata'].isin(allowed_set)) |
                (routes['arrival_iata'].isin(allowed_set))
            ].copy()

    # --- New: load city DBs (global + VN) and build iata -> city name lookup ---
    city_global = os.path.join(base_path, "city_db_cleaned.csv")
    candidates_city_vn = [
        os.path.join(base_path + "_vn", "city_db_cleaned_vn.csv"),
        os.path.join(base_path, "vn", "city_db_cleaned_vn.csv"),
        os.path.join(os.path.dirname(base_path), "cleaned_vn", "city_db_cleaned_vn.csv"),
        os.path.join("data", "cleaned_vn", "city_db_cleaned_vn.csv"),
    ]

    df_city_global = pd.read_csv(city_global) if os.path.exists(city_global) else pd.DataFrame()
    city_vn_path = next((p for p in candidates_city_vn if os.path.exists(p)), None)
    df_city_vn = pd.read_csv(city_vn_path) if city_vn_path else pd.DataFrame()

    if not df_city_global.empty or not df_city_vn.empty:
        df_cities = pd.concat([df_city_global, df_city_vn], ignore_index=True).drop_duplicates()
        # normalize column names (common names in your CSVs)
        # code column:
        for icol in ['code_iata_city', 'city_iata', 'iata_code', 'iata', 'code']:
            if icol in df_cities.columns:
                df_cities['city_code'] = df_cities[icol].astype(str)
                break
        # name column:
        for ncol in ['name_city', 'city_name', 'name']:
            if ncol in df_cities.columns:
                df_cities['city_name_norm'] = df_cities[ncol].astype(str)
                break
        if 'city_code' not in df_cities.columns:
            df_cities['city_code'] = ""
        if 'city_name_norm' not in df_cities.columns:
            df_cities['city_name_norm'] = ""
        # build lookup (uppercase keys)
        city_lookup = {
            (c.strip().upper() if isinstance(c, str) else ""): n.strip()
            for c, n in zip(df_cities['city_code'], df_cities['city_name_norm'])
            if isinstance(c, str) and c.strip()
        }
    else:
        city_lookup = {}
    # --- end new code ---
    
    # Lọc dữ liệu theo sân bay (nếu có) hoặc theo danh sách IATA của một thành phố
    if departure_filter:
        routes = routes[routes['departure_iata'].str.upper() == departure_filter.upper()]
    elif departure_city_iatas:
        # ensure uppercase compare
        iata_set = set([i.upper() for i in departure_city_iatas if isinstance(i, str) and i.strip() != ""])
        if iata_set:
            routes = routes[routes['departure_iata'].str.upper().isin(iata_set)]
        
    # Tạo từ điển lookup sân bay
    airport_dict = {
        row['iata_code']: {
            'lat': row['latitude'],
            'lon': row['longitude'],
            'name': row.get('airport_name') if 'airport_name' in row else row.get('name', ""),
            'country': row.get('country', ""),
            # attach city from city_lookup if available, fallback to any city column on airport row
            'city': city_lookup.get(str(row['iata_code']).upper())
                    or (row.get('city') if 'city' in row else row.get('municipality') if 'municipality' in row else None),
        }
        for _, row in airports.iterrows()
        if pd.notnull(row.get('latitude')) and pd.notnull(row.get('longitude')) and str(row.get('iata_code')).strip() != ""
    }
    
    # Tạo bản đồ trung tâm
    m = folium.Map(location=[21.03718016261013, 105.83462635582046], zoom_start=6, tiles="CartoDB positron", width='100%', height='100%')
    
    # Vẽ các đường bay
    for _, route in routes.iterrows():
        dep = route['departure_iata']
        arr = route['arrival_iata']
        airline = route.get('airline_iata', 'N/A')
        flight_no = route.get('flight_number', 'N/A')
        
        if dep in airport_dict and arr in airport_dict:
            dep_coords = [airport_dict[dep]['lat'], airport_dict[dep]['lon']]
            arr_coords = [airport_dict[arr]['lat'], airport_dict[arr]['lon']]
            popup_text = f"{dep} -> {arr}<br>Airline: {airline}<br>Flight: {flight_no}"
            dep_country = (airport_dict[dep].get('country') or "").strip().upper()
            arr_country = (airport_dict[arr].get('country') or "").strip().upper()
            is_domestic = (dep_country != "" and arr_country != "" and dep_country == arr_country)

            line_color = 'red' if is_domestic else 'green'

            folium.PolyLine(
                [dep_coords, arr_coords],
                color = line_color, weight = 1, opacity = 0.4,
                popup = popup_text
            ).add_to(m)
            
    # Markers cho các sân bay
    for iata, info in airport_dict.items():
        name = info.get('name', '').strip()
        city = (info.get('city') or "").strip()
        country = (info.get('country') or "").strip()

        # build popup parts only when available
        parts = []
        header = f"{iata}"
        if name:
            header = f"{header} - {name}"
        parts.append(header)
        if city:
            parts.append(f"City: {city}")
        if country:
            parts.append(country)
        popup_text = " | ".join(parts)

        # improved VN detection (accept 'VN' or 'Vietnam' or variants)
        country_up = country.upper()
        is_vn = 'VN' in country_up or 'VIET' in country_up

        # preferred: Marker with Font Awesome star icon (gold). Background color uses Folium allowed names.
        pin_color = 'red' if is_vn else 'blue'
        icon = folium.Icon(icon='star' if is_vn else 'plane', prefix='fa', icon_color='gold' if is_vn else 'white', color=pin_color)
        folium.Marker(
            [info['lat'], info['lon']],
            popup=popup_text,
            icon=icon,
            tooltip=iata
        ).add_to(m)
        
    m.save(output_path)
    print("Đã lưu bản đồ tại: ", output_path)
    return m

def create_realtime_map(
    rt_csv: str,
    ft_csv: Optional[str] = None,
    df_airports: Optional[pd.DataFrame] = None,
    only_active: bool = True,
    airline_filter: Optional[Iterable[str]] = None,
    origin_filter: Optional[str] = None,
    dest_filter: Optional[str] = None,
    max_show: int = 200,
) -> folium.Map:
    """
    Build a folium.Map showing realtime flights (animated dashed lines).
    - rt_csv: path to realtime_schedules_cleaned.csv
    - ft_csv: optional path to flight_tracker_cleaned.csv (used as fallback for coords)
    - df_airports: optional airports dataframe to resolve iata -> lat/lon (recommended)
    - filters: only_active, airline_filter (iterable), origin_filter, dest_filter
    - max_show: maximum number of flights to render
    Returns folium.Map
    """
    # load realtime file
    df_rt = pd.read_csv(rt_csv, low_memory=False) if os.path.exists(rt_csv) else pd.DataFrame()
    df_ft = pd.read_csv(ft_csv, low_memory=False) if (ft_csv and os.path.exists(ft_csv)) else pd.DataFrame()

    # helper to find candidate columns
    def find_col(df, candidates):
        return next((c for c in candidates if c in df.columns), None)

    dep_col = find_col(df_rt, ['departure_iata','orig_iata','origin_iata','origin','dep_iata','departure_airport'])
    arr_col = find_col(df_rt, ['arrival_iata','dest_iata','destination_iata','arrival','arr_iata','arrival_airport'])
    status_col = find_col(df_rt, ['status','flight_status','state'])
    airline_col = find_col(df_rt, ['airline','operator','airline_name'])

    # normalize columns into internal names
    df = df_rt.copy()
    df['__dep'] = df[dep_col].astype(str).str.upper().str.strip() if dep_col else ""
    df['__arr'] = df[arr_col].astype(str).str.upper().str.strip() if arr_col else ""
    df['__status'] = df[status_col].astype(str).str.lower().str.strip() if status_col else ""
    if airline_col:
        df[airline_col] = df[airline_col]

    # apply filters
    if only_active and status_col:
        active_values = {'active','enroute','airborne','in_flight','en-route','en route'}
        df = df[df['__status'].isin(active_values)]
    if airline_filter and airline_col:
        df = df[df[airline_col].isin(airline_filter)]
    if origin_filter:
        of = origin_filter.upper().strip()
        df = df[(df['__dep'] == of) | (df['__arr'] == of)]
    if dest_filter:
        dfst = dest_filter.upper().strip()
        df = df[(df['__arr'] == dfst) | (df['__dep'] == dfst)]

    # build airports lookup (iata -> (lat,lon,name))
    airports_lookup = {}
    if df_airports is not None and not df_airports.empty:
        for _, r in df_airports.iterrows():
            i = str(r.get('iata_code','')).upper().strip()
            if not i:
                continue
            lat = r.get('latitude') if 'latitude' in r else r.get('lat') if 'lat' in r else None
            lon = r.get('longitude') if 'longitude' in r else r.get('lon') if 'lon' in r else None
            try:
                if pd.notna(lat) and pd.notna(lon):
                    airports_lookup[i] = (float(lat), float(lon), r.get('airport_name','') or "")
            except Exception:
                continue

    # fallback resolve coords from flight_tracker file (if available)
    ft_code_col = find_col(df_ft, ['airport_iata','iata_code','icao'])
    ft_lat_col = find_col(df_ft, ['lat','latitude','airport_lat','latitude_deg'])
    ft_lon_col = find_col(df_ft, ['lon','longitude','airport_lon','longitude_deg'])

    def resolve_coords(iata: str):
        if not iata or pd.isna(iata):
            return None
        code = str(iata).upper().strip()
        if code in airports_lookup:
            lat, lon, name = airports_lookup[code]
            return (lat, lon, name)
        if ft_code_col and ft_lat_col and ft_lon_col and not df_ft.empty:
            row = df_ft[df_ft[ft_code_col].astype(str).str.upper().str.strip() == code]
            if not row.empty:
                try:
                    rr = row.iloc[0]
                    return (float(rr[ft_lat_col]), float(rr[ft_lon_col]), code)
                except Exception:
                    return None
        return None

    # collect flights (only those with resolvable coords)
    flights = []
    seen_airports = set()
    for _, r in df.iterrows():
        if len(flights) >= int(max_show):
            break
        dep = r.get('__dep'); arr = r.get('__arr')
        if not dep or not arr:
            continue
        res_dep = resolve_coords(dep); res_arr = resolve_coords(arr)
        if res_dep is None or res_arr is None:
            continue
        dep_lat, dep_lon, dep_name = res_dep
        arr_lat, arr_lon, arr_name = res_arr
        info = {
            'flight': (r.get('flight_iata') or r.get('flight_number') or r.get('callsign') or ""),
            'airline': (r.get(airline_col) if airline_col in r else ""),
            'status': (r.get(status_col) if status_col in r else "")
        }
        flights.append({'start': (dep_lat, dep_lon), 'end': (arr_lat, arr_lon), 'dep': dep, 'arr': arr, 'info': info})
        seen_airports.update({dep, arr})

    # Build map centered on flights or default
    if flights:
        avg_lat = sum((f['start'][0] + f['end'][0]) for f in flights) / (2*len(flights))
        avg_lon = sum((f['start'][1] + f['end'][1]) for f in flights) / (2*len(flights))
    else:
        avg_lat, avg_lon = 0.0, 0.0

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=4, tiles='CartoDB positron')

    # draw animated dashed lines (AntPath) for each flight
    airport_coords_used = {}
    for f in flights:
        AntPath(
            locations=[f['start'], f['end']],
            color='red',
            weight=3,
            delay=800,
            dash_array=[10, 20],
            pulse_color='gold'
        ).add_to(m)
        # popup at midpoint
        mid = ((f['start'][0] + f['end'][0]) / 2.0, (f['start'][1] + f['end'][1]) / 2.0)
        popup_html = f"{f['info'].get('airline','')} {f['info'].get('flight','')}<br>{f['dep']} → {f['arr']}<br>Status: {f['info'].get('status','')}"
        folium.Marker(location=mid, popup=popup_html, icon=folium.Icon(color='blue', icon='plane', prefix='fa')).add_to(m)
        airport_coords_used[f['dep']] = f['start']
        airport_coords_used[f['arr']] = f['end']

    # add markers only for involved airports
    for code, coord in airport_coords_used.items():
        name = code
        if df_airports is not None and 'iata_code' in df_airports.columns:
            row = df_airports[df_airports['iata_code'].astype(str).str.upper().str.strip() == code]
            if not row.empty:
                try:
                    name = row.iloc[0].get('airport_name') or code
                except Exception:
                    name = code
        folium.CircleMarker(location=coord, radius=4, color='navy', fill=True, tooltip=f"{name} ({code})").add_to(m)

    return m

if __name__ == "__main__":
    create_flight_map(
        departure_filter = "HAN"
    )
