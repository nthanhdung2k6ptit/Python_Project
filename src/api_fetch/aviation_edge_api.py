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
    
    def get_airports_database(self, code_iso2_country="VN"): 
        return self._make_request("airportDatabase", {"codeIso2Country": code_iso2_country})
    
    def get_city_database(self, code_iso2_country="VN"):
        return self._make_request("cityDatabase", {"codeIso2Country": code_iso2_country})
    
    def get_airline_database(self, code_iso2_country="VN"):
        return self._make_request("airlineDatabase", {"codeIso2Country": code_iso2_country})
    
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

    airports_vn = client.get_airports_database()
    airlines_vn = client.get_airline_database()
    cities_vn = client.get_city_database()

    client.save_to_csv(airports_vn, "airport_db_raw")
    client.save_to_csv(cities_vn, "city_db_raw")

    airline_codes = [a["codeIataAirline"] for a in airlines_vn if a.get("codeIataAirline")]
    flights_vn, routes_vn = [], []
    for code in airline_codes:
        flights_vn.extend(client.get_flight_tracker(code))
        routes_vn.extend(client.get_airline_routes(code))
    client.save_to_csv(flights_vn, "flight_tracker_raw")
    client.save_to_csv(routes_vn, "routes_raw")

    airport_codes = [a["codeIataAirport"] for a in airports_vn if a.get("codeIataAirport")]
    all_realtime = []
    for airport in airport_codes:
        all_realtime.extend(client.get_real_time_schedules(airport))
    client.save_to_csv(all_realtime, "realtime_schedules_raw")

    all_historical = []
    for airport in [a["codeIataAirport"] for a in airports_vn if a.get("codeIataAirport")]:
        data = client.get_historical_schedules(airport, "2025-09-01", "2025-09-05")
        if data: all_historical.extend(data)
    client.save_to_csv(all_historical, "historical_schedules_raw")

    client.save_to_csv(client.get_nearby_airports(21.03, 105.85, 200), "nearby_airports_raw")

    city_iata_codes = [c["codeIataCity"] for c in cities_vn if c.get("codeIataCity")]
    all_autocomplete = []
    for code_iata_city in city_iata_codes:
        data_dict = client.get_autocomplete(code_iata_city)
        if isinstance(data_dict, dict) and "airportsByCities" in data_dict:
            list_ben_trong = data_dict["airportsByCities"]
            if list_ben_trong: 
                all_autocomplete.extend(list_ben_trong)
        else:
            print(f"Không tìm thấy dữ liệu 'airportsByCities' cho {code_iata_city}")
    client.save_to_csv(all_autocomplete, "autocomplete_raw")





