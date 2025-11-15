
import pandas as pd
import folium
import os


def create_flight_map(
    base_path = "data/cleaned",
    output_path = "data/reports/flight_routes_map.html",
    departure_filter = None,
    departure_city_iatas = None,
    allowed_iatas = None
):
    airport_global = os.path.join(base_path, "airport_db_cleaned.csv")
    routes_global = os.path.join(base_path, "routes_cleaned.csv")

    candidates_air_vn = [
        os.path.join(base_path + "_vn", "airport_db_cleaned_vn.csv"),      
        os.path.join(base_path, "vn", "airport_db_cleaned_vn.csv"),   
        os.path.join(os.path.dirname(base_path), "cleaned_vn", "airport_db_cleaned_vn.csv"),
        os.path.join("data", "cleaned_vn", "airport_db_cleaned_vn.csv"),
    ]
    candidates_routes_vn = [
        os.path.join(base_path + "_vn", "routes_cleaned_vn.csv"),
        os.path.join(base_path, "vn", "routes_cleaned_vn.csv"),
        os.path.join(os.path.dirname(base_path), "cleaned_vn", "routes_cleaned_vn.csv"),
        os.path.join("data", "cleaned_vn", "routes_cleaned_vn.csv"),
    ]

    df_air_global = pd.read_csv(airport_global)
    df_route_global = pd.read_csv(routes_global)
    
    airport_vn = next((p for p in candidates_air_vn if os.path.exists(p)), None)
    routes_vn = next((p for p in candidates_routes_vn if os.path.exists(p)), None)

    if airport_vn:
        df_air_vn = pd.read_csv(airport_vn)
        df_air_vn['country'] = 'Vietnam'
        df_air_vn['__src'] = 'vn'
    else:
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
    
    airports = pd.concat([df_air_global, df_air_vn]).drop_duplicates(subset=['iata_code'])
    routes = pd.concat([df_route_global, df_route_vn]).drop_duplicates(subset=['departure_iata', 'arrival_iata'])
 
    if 'iata_code' in airports.columns:
        airports['iata_code'] = airports['iata_code'].astype(str).str.upper().str.strip()
    if 'departure_iata' in routes.columns:
        routes['departure_iata'] = routes['departure_iata'].astype(str).str.upper().str.strip()
    if 'arrival_iata' in routes.columns:
        routes['arrival_iata'] = routes['arrival_iata'].astype(str).str.upper().str.strip()

    if allowed_iatas is not None:
        allowed_set = {s.upper().strip() for s in allowed_iatas if isinstance(s, str) and s.strip()}
        
        if 'iata_code' in airports.columns:
            airports = airports[airports['iata_code'].isin(allowed_set)].copy()
        
        if not routes.empty:
            routes = routes[
                (routes['departure_iata'].isin(allowed_set)) |
                (routes['arrival_iata'].isin(allowed_set))
            ].copy()

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
        
        for icol in ['code_iata_city', 'city_iata', 'iata_code', 'iata', 'code']:
            if icol in df_cities.columns:
                df_cities['city_code'] = df_cities[icol].astype(str)
                break
            
        for ncol in ['name_city', 'city_name', 'name']:
            if ncol in df_cities.columns:
                df_cities['city_name_norm'] = df_cities[ncol].astype(str)
                break
        if 'city_code' not in df_cities.columns:
            df_cities['city_code'] = ""
        if 'city_name_norm' not in df_cities.columns:
            df_cities['city_name_norm'] = ""
            
            
        city_lookup = {
            (c.strip().upper() if isinstance(c, str) else ""): n.strip()
            for c, n in zip(df_cities['city_code'], df_cities['city_name_norm'])
            if isinstance(c, str) and c.strip()
        }
    else:
        city_lookup = {}
    
    if departure_filter:
        routes = routes[routes['departure_iata'].str.upper() == departure_filter.upper()]
    elif departure_city_iatas:
        iata_set = set([i.upper() for i in departure_city_iatas if isinstance(i, str) and i.strip() != ""])
        if iata_set:
            routes = routes[routes['departure_iata'].str.upper().isin(iata_set)]
        
    airport_dict = {
        row['iata_code']: {
            'lat': row['latitude'],
            'lon': row['longitude'],
            'name': row.get('airport_name') if 'airport_name' in row else row.get('name', ""),
            'country': row.get('country', ""),
            
            'city': city_lookup.get(str(row['iata_code']).upper())
                    or (row.get('city') if 'city' in row else row.get('municipality') if 'municipality' in row else None),
        }
        for _, row in airports.iterrows()
        if pd.notnull(row.get('latitude')) and pd.notnull(row.get('longitude')) and str(row.get('iata_code')).strip() != ""
    }
    
    m = folium.Map(location=[21.03694437292556, 105.83466574010916], zoom_start=6, tiles="CartoDB positron", width='100%', height='100%')
    
    # vẽ
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
            
    # markers
    for isata, info in airport_dict.items():
        name = info.get('name', '').strip()
        city = (info.get('city') or "").strip()
        country = (info.get('country') or "").strip()

        parts = []
        header = f"{isata}"
        if name:
            header = f"{header} - {name}"
        parts.append(header)
        if city:
            parts.append(f"City: {city}")
        if country:
            parts.append(country)
        popup_text = " | ".join(parts)

        country_up = country.upper()
        is_vn = 'VN' in country_up or 'VIET' in country_up

        pin_color = 'red' if is_vn else 'blue'
        icon = folium.Icon(icon='star' if is_vn else 'plane', prefix='fa', icon_color='gold' if is_vn else 'white', color=pin_color)
        folium.Marker(
            [info['lat'], info['lon']],
            popup=popup_text,
            icon=icon,
            tooltip=isata
        ).add_to(m)
        
    m.save(output_path)
    print("Đã lưu bản đồ tại: ", output_path)
    return m

