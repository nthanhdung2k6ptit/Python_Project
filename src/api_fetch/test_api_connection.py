# Class & functions lấy dữ liệu từ API Aviation Edge
import requests
import json
import pandas as pd
import os
from datetime import datetime

class AviationEdgeAPI:
    def __init__ (self, api_key):
        self.api_key = api_key
        self.base_url = "http://aviation-edge.com/v2/public/"

    def get_flight_tracker(self, airline_iata=None, limit=100, offset=0):
        if airline_iata is None: return []
        return self._make_request("flights", {"airlineIata": airline_iata, "limit": limit, "offset": offset})
    
    def get_real_time_schedules(self, airport_iata_code, schedule_type="departure"):
        return self._make_request("timetable", {"iataCode": airport_iata_code, "type": schedule_type})
    
    def get_historical_schedules(self, airport_iata_code, date_from, date_to, schedule_type="departure"):
        if (datetime.strptime(date_to, "%Y-%m-%d") - datetime.strptime(date_from, "%Y-%m-%d")).days > 30:
            print("Khoảng thời gian vượt quá 30 ngày. Vui lòng rút ngắn lại.")
            return []         
        return self._make_request("flightsHistory", {
            "iataCode": airport_iata_code,
            "date_from": date_from,
            "date_to": date_to,
            "type": schedule_type
        })
    
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
            print("--- Lấy dữ liệu thành công! ---")
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

    countries = client.get_country_database()
    if not countries:
        print("Không thể lấy danh sách quốc gia.")
        exit()

    all_airlines, all_routes, all_flights, all_realtime = [], [], [], []
    all_airports, all_cities = [], []

    # --- 2. Lặp qua từng quốc gia ---
    for idx, country in enumerate(countries, start=1):
        code = country.get("codeIso2Country")
        name = country.get("nameCountry")
        if not code:
            continue

        print(f"\n [{idx}/{len(countries)}] Đang xử lý quốc gia: {name} ({code})")

        # Lấy dữ liệu gốc
        airlines = client.get_airline_database(code_iso2_country=code)
        airports = client.get_airports_database(code_iso2_country=code)
        cities = client.get_city_database(code_iso2_country=code)

        if airlines: all_airlines.extend(airlines)
        if airports: all_airports.extend(airports)
        if cities: all_cities.extend(cities)

        # --- Chỉ lấy thêm flight/route/realtime cho các quốc gia có dữ liệu airline ---
        if not airlines or not airports:
            print(f"Thiếu airline hoặc airport ở {code}, bỏ qua flights/routes/realtime.")
            continue

        # Lấy tối đa 10 hãng & sân bay đại diện
        airline_codes = [a["codeIataAirline"] for a in airlines if a.get("codeIataAirline")][:10]
        airport_codes = [a["codeIataAirport"] for a in airports if a.get("codeIataAirport")][:10]

        for airline in airline_codes:
            flights = client.get_flight_tracker(airline_iata=airline)
            if flights: all_flights.extend(flights)

            routes = client.get_airline_routes(airline_iata=airline)
            if routes: all_routes.extend(routes)

        for airport in airport_codes:
            realtime = client.get_real_time_schedules(airport)
            if realtime: all_realtime.extend(realtime)
        
        all_autocomplete = []
        for idx, city in enumerate(cities, start=1):
            name_city = city.get("nameCity")
            if not name_city:
               continue

            print(f"[{idx}] Đang tìm sân bay cho: {name_city}")
            data = client.get_autocomplete(name_city)

    # Dữ liệu hợp lệ
            if isinstance(data, dict) and "airportsByCities" in data:
               all_autocomplete.extend(data["airportsByCities"])

    # Giới hạn thử nghiệm để tránh tốn quota (ví dụ: chỉ 10 thành phố đầu)
            if idx >= 10:
               break

    # --- 3. Lưu toàn bộ dữ liệu ---
    client.save_to_csv(all_airports, "airport__db_raw")
    client.save_to_csv(all_cities, "city_db_raw")
    client.save_to_csv(all_routes, "routes_raw")
    client.save_to_csv(all_flights, "flight_tracker_raw")
    client.save_to_csv(all_realtime, "realtime_schedules_raw")
    client.save_to_csv(all_autocomplete, "autocomplete_raw")
    client.save_to_csv(client.get_nearby_airports(21.03, 105.85, 200), "nearby_airports_raw")

# tổng 20 000 chuyến bay