# Class & functions lấy dữ liệu từ API Aviation Edge
import requests
import json
import pandas as pd
import os
class AviationEdgeAPI:
    def __init__ (self, api_key):
        self.api_key = api_key
        self.base_url = "http://aviation-edge.com/v2/public/"

    def get_flights(self, iataCode=None):
        endpoint = "flights"
        params = {}
        if iataCode:
            params['iataCode'] = iataCode
        return self._make_request(endpoint, params=params)
    
    def get_airline_routes(self, airline_iata_code):
        endpoint = "routes"
        params = {"airlineIataCode": airline_iata_code}
        return self._make_request(endpoint, params)
    
    def get_real_time_schedules(self, airport_iata_code, schedule_type="departure"):
        endpoint = "timetable" 
        params = {
            "iataCode": airport_iata_code,
            "type": schedule_type 
        }
        return self._make_request(endpoint, params)
    
    def get_nearby_airports(self, latitude, longitude, distance):
        endpoint = "nearby"
        params = {"lat": latitude, "lng": longitude, "distance": distance}
        return self._make_request(endpoint, params)
    
    def get_historical_schedules(self, airport_iata_code, flight_date, schedule_type="departure"):
        endpoint = "flightsHistory"
        params = {"iataCode": airport_iata_code, "type": schedule_type, "date": flight_date}
        return self._make_request(endpoint, params=params)
    
    def get_future_schedules(self, airport_iata_code, flight_date, schedule_type="departure"):
        endpoint = "futureTimetable"
        params = {"iataCode": airport_iata_code, "type": schedule_type, "date": flight_date}
        return self._make_request(endpoint, params=params)
    
    def get_autocomplete(self, search_term, search_type="airport"):
        endpoint = "autocomplete"
        params = {"term": search_term, "type": search_type}
        return self._make_request(endpoint, params=params)
    
    def get_satellite_tracker(self, satellite_name):
        endpoint = "satellites"
        params = {"search": satellite_name} 
        return self._make_request(endpoint, params=params)
    
    def get_airline_database(self, airline_iata_code):
        endpoint = "airlineDatabase"
        params = {"iataCode": airline_iata_code}
        return self._make_request(endpoint, params=params)
    
    def get_airport_database(self, airport_iata_code):
        endpoint = "airportDatabase"
        params = {"iataCode": airport_iata_code}
        return self._make_request(endpoint, params=params)
    
    def _make_request(self, endpoint, params=None):
        if params is None:
            params = {}
        params["key"] = self.api_key
        url = self.base_url + endpoint
        try:
            response = requests.get(url, params=params, timeout=10)
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

        folder_path = r"C:\Users\ADMIN\Graph_Network_Project\data"
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{filename}.csv")

        # Chuyển dữ liệu JSON sang DataFrame
        try:
            df = pd.json_normalize(data)  
            df.to_csv(file_path, index=False, encoding="utf-8-sig")
            print(f"Đã lưu file: {file_path}")
        except Exception as e:
            print(f"Lỗi khi lưu {filename}: {e}")

if __name__ == "__main__":
    api_key = "96b7d0-5b0bc0"  
    client = AviationEdgeAPI(api_key)
    tasks = [
        (client.get_flights, {}, "flights_raw"),
        (client.get_airline_routes, {"airline_iata_code": "VN"}, "routes_raw"),
        (client.get_real_time_schedules, {"airport_iata_code": "HAN"}, "realtime_schedules_raw"),
        (client.get_nearby_airports, {"latitude": 21.03, "longitude": 105.85, "distance": 100}, "nearby_airports_raw"),
        (client.get_historical_schedules, {"airport_iata_code": "HAN", "flight_date": "2024-10-01"}, "historical_schedules_raw"),
        (client.get_future_schedules, {"airport_iata_code": "HAN", "flight_date": "2024-12-01"}, "future_schedules_raw"),
        (client.get_autocomplete, {"search_term": "Noi Bai"}, "autocomplete_raw"),
        (client.get_satellite_tracker, {"satellite_name": "Starlink"}, "satellite_raw"),
        (client.get_airline_database, {"airline_iata_code": "VN"}, "airline_db_raw"),
        (client.get_airport_database, {"airport_iata_code": "HAN"}, "airport_db_raw"),
    ]

    for func, params, filename in tasks:
        print(f"\n Đang lấy dữ liệu cho: {filename}")
        data = func(**params)
        client.save_to_csv(data, filename)




