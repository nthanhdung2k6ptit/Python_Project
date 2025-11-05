# Folium vẽ bản đồ, routes

import folium
import pandas as pd

def draw_routes(data_path = "data/cleanded/routes_clean.csv" save_path = "data/reports/map.html", city = None):
    # Doc du lieu tu file CSV
    df = pd.read_csv(data_path)
    
    # Loc du lieu theo thanh pho neu can
    if city:
        df = df[(df['origin'] == city) | (df['destination'] == city)]

    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

for _, row in df.iterrows():
    folium.PolyLine(
        [(row['origin_lat'], row['origin_loon']), (row['dest_lat'], row['dest_lon'])],
        color="blue", weight=1, opacity=0.7
    ).add_to(m)

# Danh dau airports
for city_code, lat, lon in zip(df['origin'], df['origin_lat'], df['origin_lon']):
    folium.CircleMarker(location=[lat, lon], redius=3, color="red", fill=True),add_to(m)

m.save(save_path)

return m