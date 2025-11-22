import pandas as pd
import folium
from folium import plugins
from folium.plugins import AntPath
import webbrowser
import os

def load_flight_data(csv_path='data/cleaned_vn/flight_tracker_live_vn_cleaned_vn.csv'):
    try:
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError:
        print(f"Error: Không tìm thấy file {csv_path}")
        return None


def get_airport_coordinates():
    airports = {
        'SGN': {'lat': 10.8188, 'lon': 106.6519, 'name': 'Tân Sơn Nhất'},
        'HAN': {'lat': 21.2212, 'lon': 105.8066, 'name': 'Nội Bài'},
        'DAD': {'lat': 16.0439, 'lon': 108.1994, 'name': 'Đà Nẵng'},
        'CXR': {'lat': 12.0119, 'lon': 109.2194, 'name': 'Cam Ranh'},
        'PQC': {'lat': 10.1698, 'lon': 103.9932, 'name': 'Phú Quốc'},
        'HPH': {'lat': 20.8194, 'lon': 106.7250, 'name': 'Cát Bi'},
        'HUI': {'lat': 16.4015, 'lon': 107.7033, 'name': 'Huế'},
        'UIH': {'lat': 13.9550, 'lon': 109.0422, 'name': 'Quy Nhơn'},
        'VCA': {'lat': 12.2165, 'lon': 109.1926, 'name': 'Vân Đồn'},
        'DLI': {'lat': 11.7503, 'lon': 108.3672, 'name': 'Đà Lạt'},
        'TBB': {'lat': 12.6306, 'lon': 107.3547, 'name': 'Tuy Hòa'},
        'BMV': {'lat': 12.6679, 'lon': 108.1203, 'name': 'Buôn Ma Thuột'},
        'THD': {'lat': 19.9012, 'lon': 105.4679, 'name': 'Thanh Hóa'},
        'BKK': {'lat': 13.6900, 'lon': 100.7501, 'name': 'Bangkok'},
        'SIN': {'lat': 1.3644, 'lon': 103.9915, 'name': 'Singapore'},
        'KUL': {'lat': 2.7456, 'lon': 101.7099, 'name': 'Kuala Lumpur'},
        'ICN': {'lat': 37.4602, 'lon': 126.4407, 'name': 'Incheon'},
        'NRT': {'lat': 35.7647, 'lon': 140.3864, 'name': 'Tokyo Narita'},
        'SYD': {'lat': -33.9399, 'lon': 151.1753, 'name': 'Sydney'},
        'MEL': {'lat': -37.6690, 'lon': 144.8410, 'name': 'Melbourne'},
        'LHR': {'lat': 51.4700, 'lon': -0.4543, 'name': 'London Heathrow'},
        'DPS': {'lat': -8.7467, 'lon': 115.1671, 'name': 'Bali Denpasar'},
        'CGK': {'lat': -6.1256, 'lon': 106.6559, 'name': 'Jakarta'},
        'HKG': {'lat': 22.3080, 'lon': 113.9185, 'name': 'Hong Kong'},
        'TPE': {'lat': 25.0797, 'lon': 121.2342, 'name': 'Taipei'},
        'CAN': {'lat': 23.3924, 'lon': 113.2988, 'name': 'Guangzhou'},
        'PUS': {'lat': 35.1795, 'lon': 128.9388, 'name': 'Busan'},
        'KHH': {'lat': 22.5771, 'lon': 120.3498, 'name': 'Kaohsiung'},
        'NGO': {'lat': 34.8584, 'lon': 136.8052, 'name': 'Nagoya'},
        'PER': {'lat': -31.9403, 'lon': 115.9672, 'name': 'Perth'},
        'LPQ': {'lat': 19.8973, 'lon': 102.1638, 'name': 'Luang Prabang'},
        'CNX': {'lat': 18.7667, 'lon': 98.9667, 'name': 'Chiang Mai'},
        'HKT': {'lat': 8.1132, 'lon': 98.3169, 'name': 'Phuket'},
        'HDY': {'lat': 6.9333, 'lon': 100.3933, 'name': 'Hat Yai'},
        'URT': {'lat': 13.6900, 'lon': 100.7500, 'name': 'Surat Thani'},
    }
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
    
    # Thêm các máy bay đang bay với AntPath
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