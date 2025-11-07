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

    def get_flight_tracker(self, flight_iata=None, flight_icao=None, airline_iata=None, airline_icao=None, dep_iata=None, dep_icao=None, 
                           arr_iata=None, arr_icao=None, status=None, limit=100, offset=0):
        endpoint = "flights"
        params = {
        "flightIata": flight_iata,
        "flightIcao": flight_icao,
        "airlineIata": airline_iata,
        "airlineIcao": airline_icao,
        "depIata": dep_iata,
        "depIcao": dep_icao,
        "arrIata": arr_iata,
        "arrIcao": arr_icao,
        "status": status,
        "limit": limit,
        "offset": offset
    }
        return self._make_request(endpoint, params)
    
    def get_real_time_schedules(self, airport_iata_code, schedule_type="departure"):
        if isinstance(airport_iata_code, str): airport_iata_code = [airport_iata_code]
        all_schedules = []
        for airport in airport_iata_code:
            params = {
                 "iataCode": airport,
                 "type": schedule_type
            }
            data = self._make_request("timetable", params)
            if data: all_schedules.extend(data)
        return all_schedules
    
    def get_historical_schedules(self, airport_iata_code, date_from, date_to, schedule_type="departure", status=None):
        endpoint = "flightsHistory"
        params = {
        "iataCode": airport_iata_code,
        "type": schedule_type,    
        "date_from": date_from,    
        "date_to": date_to,        
        "status": status           
        }
        if (datetime.strptime(date_to, "%Y-%m-%d") - datetime.strptime(date_from, "%Y-%m-%d")).days > 30:
            print("Khoảng thời gian vượt quá 30 ngày. Vui lòng rút ngắn lại.")
            return None
        return self._make_request(endpoint, params)
    
    def get_airline_routes(self, airline_iata=None, airline_icao=None, departure_iata=None, departure_icao=None, arrival_iata=None,
                           arrival_icao=None):
        endpoint = "routes"
        params = {
        "airlineIata": airline_iata,
        "airlineIcao": airline_icao,
        "departureIata": departure_iata,
        "departureIcao": departure_icao,
        "arrivalIata": arrival_iata,
        "arrivalIcao": arrival_icao
        }
        return self._make_request(endpoint, params)
    
    def get_nearby_airports(self, lat, lng, distance=50):
        endpoint = "nearby"
        params = {
        "lat": lat,
        "lng": lng,
        "distance": distance
        }
        return self._make_request(endpoint, params)
    
    def get_autocomplete(self, city):
        if not city or len(city.strip()) < 2:
            print("Từ khóa tìm kiếm phải có ít nhất 2 ký tự.")
            return None
        endpoint = "autocomplete"
        params = {
              "city": city.strip()
        }
        return self._make_request(endpoint, params)
    
    def get_airports_database(self, code_iata_airport=None, code_icao_airport=None, code_iso2_country=None, code_iata_city=None,
                              name_airport=None):
        endpoint = "airportDatabase"
        params = {
        "codeIataAirport": code_iata_airport,
        "codeIcaoAirport": code_icao_airport,
        "codeIso2Country": code_iso2_country,
        "codeIataCity": code_iata_city,
        "nameAirport": name_airport
        }
        return self._make_request(endpoint, params)
    
    def get_city_database(self, code_iata_city=None, code_iso2_country=None, name_city=None):
        endpoint = "cityDatabase"
        params = {
        "codeIataCity": code_iata_city,
        "codeIso2Country": code_iso2_country,
        "nameCity": name_city
        }
        return self._make_request(endpoint, params)
    
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
                return None
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
    # Lấy tất cả sân bay ở Việt Nam
    airports_vn = client.get_airports_database(code_iso2_country="VN")
    airport_iata_codes_vn = [a["codeIataAirport"] for a in airports_vn if a.get("codeIataAirport")]

    tasks = [
        (client.get_flight_tracker, {"flight_iata": None, "airline_iata": "VN", "dep_iata": None, "arr_iata": None, "status": None, 
                                     "limit": 100, "offset": 0}, "flight_tracker_raw"),
        (client.get_airline_routes, {"airline_iata": "VN", "airline_icao": None, "departure_iata": None, "departure_icao": None,
                                     "arrival_iata": None, "arrival_icao": None}, "routes_raw"),
        (client.get_real_time_schedules, {"airport_iata_code": airport_iata_codes_vn, "schedule_type": None}, "realtime_schedules_raw"),
        (client.get_historical_schedules, {"airport_iata_code": "HAN", "schedule_type": "departure", "date_from": "2025-09-01",
                                           "date_to": "2025-09-30", "status": None}, "historical_schedules_raw"),
        (client.get_nearby_airports, {"lat": 21.03, "lng": 105.85, "distance": 200}, "nearby_airports_raw"),
        (client.get_autocomplete, {"city": "HAN"}, "autocomplete_raw"),
        (client.get_airports_database, {"code_iata_airport": None, "code_icao_airport": None, "code_iso2_country": None,
                                        "code_iata_city": None, "name_airport": None}, "airport_db_raw"),
        (client.get_city_database, {"code_iata_city": None, "code_iso2_country": None, "name_city": None}, "city_db_raw"),
    ]

    for func, params, filename in tasks:
        print(f"\n Đang lấy dữ liệu cho: {filename}")
        data = func(**params)
        client.save_to_csv(data, filename)




