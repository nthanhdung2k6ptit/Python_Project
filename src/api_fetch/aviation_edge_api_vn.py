# CÀO DATA RIÊNG CỦA VIỆT NAM
# Class & functions lấy dữ liệu từ API Aviation Edge
import requests
import pandas as pd
import os
import time

class AviationEdgeAPI:
    def __init__ (self, api_key):
        self.api_key = api_key
        self.base_url = "http://aviation-edge.com/v2/public/"

    def get_flight_tracker(self, airline_iata=None, limit=1000):
        if airline_iata is None: return []
        return self._make_request("flights", {"airlineIata": airline_iata, "limit": limit})
    
    def get_real_time_schedules(self, airport_iata_code, schedule_type=None):
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
    
    def get_airports_database(self, code_iso2_country="VN"): 
        return self._make_request("airportDatabase", {"codeIso2Country": code_iso2_country})
    
    def get_city_database(self, code_iso2_country="VN"):
        return self._make_request("cityDatabase", {"codeIso2Country": code_iso2_country})
    
    def get_airline_database(self, code_iso2_country="VN"):
        return self._make_request("airlineDatabase", {"codeIso2Country": code_iso2_country})
    
       
    def _clean_params(self, params):
        return {k: v for k, v in params.items() if v is not None}
    
    def _make_request(self, endpoint, params=None):
        if params is None:
            params = {}
        cleaned_params = self._clean_params(params)
        cleaned_params["key"] = self.api_key
        url = self.base_url + endpoint

        for attempt in range(2): 
            try:
                response = requests.get(url, params=cleaned_params, timeout=20)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict) and data.get('error'):
                   print(f"Lỗi từ API Aviation Edge: {data['error']}")
                   return []
                print(f"--- Lấy dữ liệu {endpoint} thành công! ---")
                return data

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 522:
                   print(f"Lỗi 522 Server Timeout, thử lại {attempt + 1}/2 ...")
                else:
                   print(f"Lỗi HTTP: {e.response.status_code} - {e}")
                   break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                print(f"Lỗi kết nối/timeout, thử lại {attempt + 1}/2 ...")
            except requests.exceptions.JSONDecodeError:
                print("Lỗi: Không thể phân tích JSON.")
                break
            except requests.exceptions.RequestException as e:
                print(f"Lỗi request không xác định: {e}") 
                break

            time.sleep(2)  # đợi 2 giây trước khi thử lại
        print(f"Không lấy được dữ liệu từ {endpoint} sau 1 lần thử lại.")
        return []  
    
    def save_to_csv(self, data, filename):
        if not data:
            print(f"Không có dữ liệu để lưu vào {filename}.")
            return

        # Đi từ vị trí file script (.../src/api_fetch)
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        # Đi lùi 2 cấp ra thư mục gốc (.../Graph_Network_Project)
        project_root = os.path.dirname(os.path.dirname(current_script_dir))
        # Đi xuôi vào .../data/raw
        folder_path = os.path.join(project_root, 'data', 'raw_vn')
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

    client.save_to_csv(airports_vn, "airport_db_raw_vn")
    client.save_to_csv(cities_vn, "city_db_raw_vn")
    client.save_to_csv(airlines_vn, "airline_db_raw_vn")

    airline_codes = [a["codeIataAirline"] for a in airlines_vn if a.get("codeIataAirline")]
    """flights_vn = []
    for code in airline_codes:
        flights_vn.extend(client.get_flight_tracker(code))
    client.save_to_csv(flights_vn, "flight_tracker_raw_vn")"""
    routes_vn = []
    for code in airline_codes:
        routes_vn.extend(client.get_airline_routes(code))
    client.save_to_csv(routes_vn, "routes_raw_vn")

    airport_codes = [a["codeIataAirport"] for a in airports_vn if a.get("codeIataAirport")]
    """all_realtime = []
    for airport in airport_codes:
        all_realtime.extend(client.get_real_time_schedules(airport))
    client.save_to_csv(all_realtime, "realtime_schedules_raw_vn")"""

    client.save_to_csv(client.get_nearby_airports(21.03, 105.85, 200), "nearby_airports_raw_vn")

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
    client.save_to_csv(all_autocomplete, "autocomplete_raw_vn")

    # Phần tự động cập nhật dữ liệu flight tracker và realtime schedules mỗi 60 giây
    flight_interval = 60              # 60 giây
    realtime_interval = 24 * 60 * 60  # 1 ngày

    last_flight_update = 0
    last_realtime_update = 0

    print("Bắt đầu tự động cập nhật dữ liệu...")

    try:
        while True:
            now = time.time()

            # 1. FLIGHT TRACKER → cập nhật mỗi 60 giây
            if now - last_flight_update >= flight_interval:
                print("\n--- CẬP NHẬT FLIGHT TRACKER (60 giây) ---")
                flights_live = []
                for i, code in enumerate(airline_codes, 1):
                    print(f"[{i}/{len(airline_codes)}] Lấy flighttracker cho: {code}")
                    flight_data = client.get_flight_tracker(code, limit=500)
                    if flight_data is not None:
                        flights_live.extend(flight_data)
                    time.sleep(0.6)

                client.save_to_csv(flights_live, "flight_tracker_live_vn")
                last_flight_update = now
                print("Đã cập nhật Flight Tracker. Chờ 60s đến lần cập nhật tiếp theo.")

            # 2. REALTIME SCHEDULES → cập nhật 1 lần 1 ngày
            if now - last_realtime_update >= realtime_interval:
                print("\n--- CẬP NHẬT REALTIME SCHEDULES (1 ngày) ---")
                all_realtime_live = []
                for i, codeIataAirport in enumerate(airport_codes, 1):
                    print(f"[{i}/{len(airport_codes)}] Lấy realtime cho: {codeIataAirport}")
                    data = client.get_real_time_schedules(codeIataAirport)
                    if data: 
                       all_realtime_live.extend(data)
                    time.sleep(0.6)

                client.save_to_csv(all_realtime_live, "realtime_schedules_live_vn")
                last_realtime_update = now
                print("Đã cập nhật Realtime Schedules. Chờ 1 ngày đến lần cập nhật tiếp theo.")

            time.sleep(1)  

    except KeyboardInterrupt:
        print("\n--- Dừng chương trình. ---")
    except Exception as e:
        print(f"\n--- Lỗi trong vòng lặp chính: {e} ---")


    
   