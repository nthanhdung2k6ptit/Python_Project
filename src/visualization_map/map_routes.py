#Import data từ file airports_db_cleaned.csv và routes_cleaned.csv

#1. File 1 | Các cột Dũng sử dụng: iata_code, latitude, longitude, airport_name, country (optional), city_iata (optional)

#2. File 2 | Các cột Dũng sử dụng: departure_iata, arrival_iata, flight_number (popup), airline_iata

import pandas as pd
import folium
import os

def create_flight_map(
    base_path = "data/cleaned",
    output_path = "data/reports/flight_routes_map.html",
    departure_filter = None # Lọc theo sân bay khởi hành (nếu cần)
):
    '''
    Tạo bản đồ các đường bay (toàn cầu)
    '''
    
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
    else:
        df_air_vn = pd.DataFrame(columns=df_air_global.columns)  # empty but compatible

    if routes_vn:
        df_route_vn = pd.read_csv(routes_vn)
    else:
        df_route_vn = pd.DataFrame(columns=df_route_global.columns)
    
    # Gộp data toàn cầu và Việt Nam lại, loại bỏ trùng IATA nếu có
    airports = pd.concat([df_air_global, df_air_vn]).drop_duplicates(subset=['iata_code'])
    routes = pd.concat([df_route_global, df_route_vn]).drop_duplicates(subset=['departure_iata', 'arrival_iata'])
    
    # Lọc dữ liệu theo sân bay (nếu có)
    if departure_filter:
        routes = routes[routes['departure_iata'].str.upper() == departure_filter.upper()]
        
    # Tạo từ điển lookup sân bay
    airport_dict = {
        row['iata_code']: {
            'lat': row['latitude'],
            'lon': row['longitude'],
            'name': row['airport_name'],
            'country': row['country'],
        }
        for _, row in airports.iterrows()
        if pd.notnull(row['latitude']) and pd.notnull(row['longitude'])
    }
    
    # Tạo bản đồ trung tâm
    m = folium.Map(location=[20, 100], zoom_start=3, tiles="CartoDB positron")
    
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
            folium.PolyLine(
                [dep_coords, arr_coords],
                color = 'green', weight = 1, opacity = 0.4,
                popup = popup_text
            ).add_to(m)
            
    # Markers cho các sân bay
    for iata, info in airport_dict.items():
        folium.Marker(
            [info['lat'], info['lon']],
            radius = 3,
            color = 'red' if info['country'] == 'Vietnam' else 'gray',
            fill = True,
            fill_color = 'red' if info['country'] == 'Vietnam' else 'gray',
            popup = f"{iata} - {info['name']} ({info['country']})"
        ).add_to(m)
        
    m.save(output_path)
    print("Đã lưu bản đồ tại: ", output_path)
    return m

if __name__ == "__main__":
    create_flight_map(
        departure_filter = "HAN"  # Ví dụ lọc thử theo sân bay Nội Bài
    )
