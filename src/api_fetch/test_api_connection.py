
'''import os
import requests

#API key cho Aviation Edge
api_key = os.getenv("AVIATION_EDGE_KEY", "96b7d0-5b0bc0")

def get_airports_data():
    url = f"https://aviation-edge.com/v2/public/airports?key={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": "Request failed", "details": str(e)}
            
if __name__ == "__main__":
    print(get_airports_data())
    '''
    
"""
Aviation Edge API - Quick Test Script
Script đơn giản để test nhanh API sau khi thuê
"""

import requests
import json

API_KEY = "96b7d0-5b0bc0"

def test_api():
    #Test API lấy danh sách chuyến bay đang bay
    
    print("\n" + "="*60)
    print("ĐANG TEST AVIATION EDGE API...")
    print("="*60 + "\n")
    
    # URL của Flight Tracker API
    url = "http://aviation-edge.com/v2/public/flights"
    
    # Parameters
    params = {
        'key': API_KEY,
        'limit': 5  #Lấy tạm max 5 chuyến bay để test
    }
    
    try:
        # Gửi request
        print("Đang gửi request...")
        response = requests.get(url, params=params, timeout=10)
        
        # Check status code
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("API KEY HỢP LỆ! Kết nối thành công!\n")
            
            # Parse JSON
            flights = response.json()
            
            # Hiển thị kết quả
            print(f"Tìm thấy {len(flights)} chuyến bay đang bay:\n")
            print("-" * 60)
            
            for i, flight in enumerate(flights, 1):
                # Lấy thông tin cơ bản
                flight_number = flight.get('flight', {}).get('iataNumber', 'N/A')
                airline = flight.get('airline', {}).get('name', 'N/A')
                departure = flight.get('departure', {}).get('iataCode', 'N/A')
                arrival = flight.get('arrival', {}).get('iataCode', 'N/A')
                status = flight.get('status', 'N/A')
                
                # Vị trí
                lat = flight.get('geography', {}).get('latitude', 'N/A')
                lng = flight.get('geography', {}).get('longitude', 'N/A')
                altitude = flight.get('geography', {}).get('altitude', 'N/A')
                
                # Tốc độ
                speed = flight.get('speed', {}).get('horizontal', 'N/A')
                
                print(f"   Chuyến bay #{i}")
                print(f"   Số hiệu: {flight_number}")
                print(f"   Hãng bay: {airline}")
                print(f"   Tuyến bay: {departure} → {arrival}")
                print(f"   Trạng thái: {status}")
                print(f"   Vị trí: {lat}, {lng}")
                print(f"   Độ cao: {altitude} m")
                print(f"   Tốc độ: {speed} km/h")
                print("-" * 60)
            
            print("\nTEST THÀNH CÔNG!")
            print("API key hoạt động bình thường.")
            
        elif response.status_code == 401:
            print("LỖI: API KEY KHÔNG HỢP LỆ!")
            print("Kiểm tra lại API key.\n")
            
        elif response.status_code == 403:
            print("LỖI: KHÔNG CÓ QUYỀN TRUY CẬP!")
            print("API key có thể đã hết hạn hoặc chưa được kích hoạt.\n")
            
        elif response.status_code == 429:
            print("LỖI: QUÁ NHIỀU REQUEST!")
            print("Đã vượt quá giới hạn API calls. Chờ một chút rồi thử lại.\n")
            
        else:
            print(f" LỖI: {response.status_code}")
            print(f" Response: {response.text}\n")
            
    except requests.exceptions.Timeout:
        print(" LỖI: REQUEST TIMEOUT!")
        print(" Kết nối quá lâu, vui lòng thử lại.\n")
        
    except requests.exceptions.ConnectionError:
        print(" LỖI: KHÔNG THỂ KẾT NỐI!")
        print(" Kiểm tra kết nối internet.\n")
        
    except Exception as e:
        print(f" LỖI KHÔNG XÁC ĐỊNH: {e}\n")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    # Kiểm tra xem đã thay API key chưa
    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n" + " "*30)
        print("CẢNH BÁO: CHƯA THAY API KEY!")
        print("Vui lòng mở file và thay 'YOUR_API_KEY_HERE' bằng API key thực.")
        print(" "*30 + "\n")
    else:
        # Chạy test
        test_api()


"""
KẾT QUẢ MONG ĐỢI:
- Nếu API key hợp lệ: Sẽ hiển thị 5 chuyến bay đang bay
- Nếu lỗi: Sẽ hiển thị thông báo lỗi cụ thể

SAU KHI TEST THÀNH CÔNG:
Có thể test các API khác bằng cách thay URL:

# Test lịch bay sân bay Nội Bài:
url = "http://aviation-edge.com/v2/public/timetable"
params = {'key': API_KEY, 'iataCode': 'HAN', 'type': 'departure'}

# Test tuyến bay Vietnam Airlines:
url = "http://aviation-edge.com/v2/public/routes"
params = {'key': API_KEY, 'airlineIata': 'VN'}

# Test tìm sân bay gần Hà Nội:
url = "http://aviation-edge.com/v2/public/nearby"
params = {'key': API_KEY, 'lat': 21.0285, 'lng': 105.8542, 'distance': 100}
"""
