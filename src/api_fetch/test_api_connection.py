
# CÀO DATA TOÀN CẦU
# Class & functions lấy dữ liệu từ API Aviation Edge
import requests
import json
import pandas as pd
import os
from datetime import datetime
from collections import Counter
import random

class AviationEdgeAPI:
    def __init__ (self, api_key):
        self.api_key = api_key
        self.base_url = "http://aviation-edge.com/v2/public/"

    def get_flight_tracker(self, airline_iata=None, limit=100, offset=0):
        if airline_iata is None: return []
        return self._make_request("flights", {"airlineIata": airline_iata, "limit": limit, "offset": offset})
    
    def get_real_time_schedules(self, airport_iata_code, schedule_type="departure"):
        return self._make_request("timetable", {"iataCode": airport_iata_code, "type": schedule_type})
    
    def get_airline_routes(self, airline_iata=None):
        if airline_iata is None: return []
        return self._make_request("routes", {"airlineIata": airline_iata})
    
    def get_nearby_airports(self, lat, lng, distance=50):
        return self._make_request("nearby", {"lat": lat, "lng": lng, "distance": distance})
    
    def get_autocomplete(self, city):
        if not city or len(city.strip()) < 2:
            print("Từ khóa tìm kiếm phải có ít nhất 2 ký tự.")
            return []
        return self._make_request("autocomplete", {"city": city.strip()})
    
    def get_airports_database(self, code_iso2_country=None): 
        return self._make_request("airportDatabase", {"codeIso2Country": code_iso2_country})
    
    def get_city_database(self, code_iso2_country= None):
        return self._make_request("cityDatabase", {"codeIso2Country": code_iso2_country})
    
    def get_airline_database(self, code_iso2_country=None):
        return self._make_request("airlineDatabase", {"codeIso2Country": code_iso2_country})
    
    def get_country_database(self):
        return self._make_request("countryDatabase")
    
    def _clean_params(self, params):
        """Loại bỏ các param có giá trị None."""
        return {k: v for k, v in params.items() if v is not None}
    
    def _make_request(self, endpoint, params=None):
        if params is None:
            params = {}
        cleaned_params = self._clean_params(params)
        cleaned_params["key"] = self.api_key
        url = self.base_url + endpoint
        try:
            response = requests.get(url, params=cleaned_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and data.get('error'):
                print(f"Lỗi từ API Aviation Edge: {data['error']}")
                return []
            print(f"--- Lấy dữ liệu {endpoint} thành công! ---")
            return data
        except requests.exceptions.HTTPError as e:
            # Lỗi này xảy ra khi key sai (401), hoặc hết hạn (403)
            print(f"Lỗi HTTP: {e.response.status_code} - {e}")
        except requests.exceptions.ConnectionError:
            print(f"Lỗi kết nối: Không thể kết nối tới server.")
        except requests.exceptions.Timeout:
            print("Lỗi: Request hết thời gian chờ (timeout).")
        except requests.exceptions.JSONDecodeError:
            print("Lỗi: Không thể phân tích JSON (server có thể trả về HTML).")
        except requests.exceptions.RequestException as e:
            print(f"Lỗi request không xác định: {e}") 
        return None
    
    def save_to_csv(self, data, filename):
        if not data:
            print(f"Không có dữ liệu để lưu vào {filename}.")
            return

        #folder_path = r"C:\Users\ADMIN\Graph_Network_Project\data\raw"   ### Dũng Note: Cái này là đường dẫn tĩnh, chỉ ai viết file này mới dùng được thôi nhé. Để cả nhóm đều chạy được trên máy của mình thì nên để đường dẫn động, lấy luôn vị trí của folder dự án
        
        # Đi từ vị trí file script (.../src/api_fetch)
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        # Đi lùi 2 cấp ra thư mục gốc (.../Graph_Network_Project)
        project_root = os.path.dirname(os.path.dirname(current_script_dir))
        # Đi xuôi vào .../data/raw
        folder_path = os.path.join(project_root, 'data', 'raw')
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{filename}.csv")

        if isinstance(data, dict) and "airportsByCities" in data: data_to_save = data["airportsByCities"]
        else: data_to_save = data
        
        # Chuyển dữ liệu JSON sang DataFrame
        try:
            df = pd.json_normalize(data_to_save)  
            df.to_csv(file_path, index=False, encoding="utf-8-sig")
            print(f"Đã lưu file: {file_path}")
        except Exception as e:
            print(f"Lỗi khi lưu {filename}: {e}")

if __name__ == "__main__":
    api_key = "96b7d0-5b0bc0"  
    client = AviationEdgeAPI(api_key)

    # --- 1. LẤY DATABASE QUỐC GIA --- 
    countries = client.get_country_database()
    if not countries:
        print("Không thể lấy danh sách quốc gia. Dừng chương trình.")
        exit()

    # --- 2. LẤY CÁC DATABASE CẦN THIẾT (SÂN BAY, THÀNH PHỐ, HÃNG BAY) ---
    all_airlines, all_airports, all_cities = [], [], []

    for country in countries:
        code = country.get("codeIso2Country")
        if code:
           airports = client.get_airports_database(code)
           cities = client.get_city_database(code)
           airlines = client.get_airline_database(code)

           if airports: all_airports.extend(airports)
           if cities: all_cities.extend(cities)
           if airlines: all_airlines.extend(airlines)

    client.save_to_csv(all_airports, "airport_db_raw")
    client.save_to_csv(all_cities, "city_db_raw")
    client.save_to_csv(all_airlines, "airline_db_raw")

    # --- 3. LẤY DỮ LIỆU REALTIME ---
    all_airports = pd.read_csv("data/raw/airport_db_raw.csv").to_dict(orient="records")
    valid_airports = [
        ap for ap in all_airports 
        if ap.get("codeIataAirport") and len(ap["codeIataAirport"]) == 3
    ]

    if len(valid_airports) < 500:
        selected_airports = valid_airports
        print(f"Chỉ có {len(valid_airports)} sân bay hợp lệ → lấy hết")
    else:
        random.shuffle(valid_airports)
        selected_airports = valid_airports[:500]
    all_realtime = []
    # Lấy 500 sân bay ngẫu nhiên từ list 'all_airports'
    random.shuffle(selected_airports)  # Trộn ngẫu nhiên toàn bộ danh sách
    for i, airport in enumerate(selected_airports[:500], 1):  
        airport_code = airport.get("codeIataAirport")
        country_code = airport.get("codeIso2Country")  # lấy code quốc gia

        print(f"[{i}/{len(selected_airports)}] Lấy realtime cho sân bay: {airport_code}, Quốc gia: ({country_code})")

        if airport_code:
           realtime = client.get_real_time_schedules(airport_code)
           if realtime: 
              all_realtime.extend(realtime)
    client.save_to_csv(all_realtime, "realtime_schedules_raw")

    # --- 4. LẤY FLIGHTS/ROUTES CHO HÃNG BAY ---
    top_airlines = [
    "AA","DL","UA","WN","EK","LH","AF","BA","CX","QR",
    "CZ","MU","CA","SQ","TK","JL","KE","NH","QF","SU",
    "AC","AS","B6","F9","FR","EY","KL","AI","BR","SK"
    ]
    all_flights, all_routes = [], []

    for i, code in enumerate(top_airlines, 1):
        print(f"[{i}/{len(top_airlines)}] Hãng: {code}")

        # 1. FLIGHT TRACKER (live)
        flights = client.get_flight_tracker(code, limit=1000)
        if flights:
            all_flights.extend(flights)
            print(f"Flight: {len(flights)} chuyến")

        # 2. ROUTES
        routes = client.get_airline_routes(code)
        if routes:
            all_routes.extend(routes)
            print(f"Routes: {len(routes)} tuyến")
        else:
            print(f"Không có routes cho {code}")

    client.save_to_csv(all_flights, "flight_tracker_raw")
    client.save_to_csv(all_routes, "routes_raw")

    # --- 5. CÁC API CÒN LẠI ---
    # Autocomplete 
    top_autocomplete_countries = countries[:10]
    all_autocomplete = []
    autocomplete_city_codes = [c["codeIataCity"] for c in all_cities if c.get("codeIataCity") and c.get("codeIso2Country") in {co.get("codeIso2Country") for co in top_autocomplete_countries}][:10]
    
    for city_code in autocomplete_city_codes:
        data = client.get_autocomplete(city_code) 
        if isinstance(data, dict) and "airportsByCities" in data:
             all_autocomplete.extend(data["airportsByCities"])
    client.save_to_csv(all_autocomplete, "autocomplete_raw")

    # Nearby Airports
    nearby = client.get_nearby_airports(21.03, 105.85, 200)
    client.save_to_csv(nearby, "nearby_airports_raw")

    

