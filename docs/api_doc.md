# Ghi chú về API
DANH SÁCH API SẼ ĐƯỢC CHÚNG TA DÙNG

# 1. FLIGHT TRACKER API
Mô tả: Theo dõi vị trí máy bay real-time trên toàn thế giới (lấy chuyến bay đang hoạt động)
Dữ liệu:

Vị trí hiện tại (latitude, longitude, altitude, direction)
Tốc độ (ngang và dọc)
Thông tin chuyến bay (số hiệu, IATA, ICAO)
Sân bay khởi hành/hạ cánh
Hãng bay
Loại máy bay
Trạng thái chuyến bay
Squawk code
Cập nhật mỗi vài phút

Use case: Live flight map, traffic analysis, delay detection

# 2. REAL-TIME SCHEDULES API
Mô tả: Lịch (hiển thị) chuyến bay đến/đi của sân bay HIỆN TẠI
Dữ liệu:

Trạng thái: active, scheduled, landed, cancelled, incident, diverted
Sân bay (IATA, ICAO)
Terminal & Gate
Giờ dự kiến/thực tế khởi hành/hạ cánh
Delay (nếu có)
Thông tin hãng bay
Số hiệu chuyến bay

Use case: Airport departure/arrival boards, booking platforms

# 3. AIRLINE ROUTES API
Mô tả: Tất cả tuyến bay của các hãng hàng không. Tạo tuyến bay (edges) trong đồ thị
Dữ liệu:

Sân bay đi/đến (IATA, ICAO)
Terminal
Thời gian bay
Hãng bay vận hành
Số hiệu chuyến bay
Số đăng ký máy bay

Use case: Route analysis, competitor research, network planning

# 4. NEARBY AIRPORTS API (API mở rộng thêm)
Mô tả: Tìm sân bay/thành phố gần tọa độ GPS / Tìm các sân bay gần một điểm tọa độ (lat/lng).
Dữ liệu:

Loại địa điểm: airport, railway, bus station, heliport, seaport
IATA, ICAO codes
Tên sân bay/thành phố
Tọa độ (lat, lng)
Khoảng cách từ điểm tìm kiếm
Quốc gia

Use case: Alternative airports, travel apps, location-based services

# 5. AUTOCOMPLETE API
Mô tả: Gợi ý tìm kiếm (tên) sân bay/thành phố khi gõ
Dữ liệu:

Loại: city, airport, railway, heliport...
IATA, ICAO codes
Tên đầy đủ
Thành phố, quốc gia
Tọa độ
Timezone

Use case: Search boxes, booking forms, user input assistance

# 6. AIRPORTS DATABASE API
Mô tả: Database tất cả sân bay, helipad, seaport thế giới. Cung cấp toạ độ & tên sân bay (nodes)
Dữ liệu:

Tên sân bay
IATA, ICAO codes
Tên dịch (nhiều ngôn ngữ)
Quốc gia, thành phố
Tọa độ (lat, lng)
Timezone, GMT offset
Geoname ID
Website, phone
Danh sách tuyến bay

Use case: Airport lookups, mapping, travel apps

# 7. CITY DATABASE API
Mô tả: Database tất cả thành phố có liên quan hàng không. Gắn sân bay vào thành phố tương ứng.
Dữ liệu:

Tên thành phố
IATA code
Quốc gia (ISO-2)
Tọa độ (lat, lng)
Timezone, GMT offset
Geoname ID
Tên dịch

Use case: City lookups, travel planning

# 8. AIRLINE DATABASE API
Mô tả: Database hãng bay
...
======================================================================================================
 
 1. FLIGHT TRACKER API
Endpoint: http://aviation-edge.com/v2/public/flights
Parameters:

key - API key (required)
flightIata - Lọc theo số hiệu chuyến bay (VD: VN123)
flightIcao - Lọc theo ICAO
airlineIata - Lọc theo hãng bay
airlineIcao - Lọc theo ICAO hãng
depIata - Lọc theo sân bay đi
depIcao - Lọc theo ICAO sân bay đi
arrIata - Lọc theo sân bay đến
arrIcao - Lọc theo ICAO sân bay đến
status - Lọc theo trạng thái
limit - Giới hạn số kết quả
offset - Phân trang

Example:
http://aviation-edge.com/v2/public/flights?key=YOUR_KEY&limit=100
http://aviation-edge.com/v2/public/flights?key=YOUR_KEY&flightIata=VN123
http://aviation-edge.com/v2/public/flights?key=YOUR_KEY&airlineIata=VN

2. REAL-TIME SCHEDULES API
Endpoint: http://aviation-edge.com/v2/public/timetable
Parameters:

key - API key (required)
iataCode - IATA code sân bay (required) (VD: HAN, SGN)
type - "departure" hoặc "arrival" (required)

Example:
http://aviation-edge.com/v2/public/timetable?key=YOUR_KEY&iataCode=HAN&type=departure
http://aviation-edge.com/v2/public/timetable?key=YOUR_KEY&iataCode=SGN&type=arrival

3. AIRLINE ROUTES API
Endpoint: http://aviation-edge.com/v2/public/routes
Parameters:

key - API key (required)
airlineIata - IATA code hãng bay (optional)
airlineIcao - ICAO code hãng bay (optional)
departureIata - Sân bay đi (optional)
departureIcao - ICAO sân bay đi (optional)
arrivalIata - Sân bay đến (optional)
arrivalIcao - ICAO sân bay đến (optional)

Example:
http://aviation-edge.com/v2/public/routes?key=YOUR_KEY&airlineIata=VN
http://aviation-edge.com/v2/public/routes?key=YOUR_KEY&departureIata=HAN&arrivalIata=BKK
http://aviation-edge.com/v2/public/routes?key=YOUR_KEY&departureIata=HAN

4. NEARBY AIRPORTS API
Endpoint: http://aviation-edge.com/v2/public/nearby
Parameters:

key - API key (required)
lat - Latitude (required)
lng - Longitude (required)
distance - Khoảng cách tối đa (km) (optional, default: 50)

Example:
http://aviation-edge.com/v2/public/nearby?key=YOUR_KEY&lat=21.0285&lng=105.8542&distance=100
http://aviation-edge.com/v2/public/nearby?key=YOUR_KEY&lat=10.8231&lng=106.6297&distance=50

5. AUTOCOMPLETE API
Endpoint: http://aviation-edge.com/v2/public/autocomplete
Parameters:

key - API key (required)
name - Từ khóa tìm kiếm (required, min 2 ký tự)

Example:
http://aviation-edge.com/v2/public/autocomplete?key=YOUR_KEY&name=han
http://aviation-edge.com/v2/public/autocomplete?key=YOUR_KEY&name=saigon
http://aviation-edge.com/v2/public/autocomplete?key=YOUR_KEY&name=JFK

6. AIRPORTS DATABASE API
Endpoint: http://aviation-edge.com/v2/public/airportDatabase
Parameters:

key - API key (required)
codeIataAirport - IATA code sân bay (optional)
codeIcaoAirport - ICAO code sân bay (optional)
codeIso2Country - ISO-2 country code (optional)
codeIataCity - IATA code thành phố (optional)
nameAirport - Tên sân bay (optional)

Example:
http://aviation-edge.com/v2/public/airportDatabase?key=YOUR_KEY
http://aviation-edge.com/v2/public/airportDatabase?key=YOUR_KEY&codeIataAirport=HAN
http://aviation-edge.com/v2/public/airportDatabase?key=YOUR_KEY&codeIso2Country=VN
http://aviation-edge.com/v2/public/airportDatabase?key=YOUR_KEY&codeIataCity=HAN

7. CITY DATABASE API
Endpoint: http://aviation-edge.com/v2/public/cityDatabase
Parameters:

key - API key (required)
codeIataCity - IATA code thành phố (optional)
codeIso2Country - ISO-2 country code (optional)
nameCity - Tên thành phố (optional)

Example:
http://aviation-edge.com/v2/public/cityDatabase?key=YOUR_KEY
http://aviation-edge.com/v2/public/cityDatabase?key=YOUR_KEY&codeIataCity=HAN
http://aviation-edge.com/v2/public/cityDatabase?key=YOUR_KEY&codeIso2Country=VN


8. AIRLINE DATABASE API
Endmoint: https://aviation-edge.com/v2/public/airlineDatabase

Example: https://aviation-edge.com/v2/public/airlineDatabase?key=96b7d0-5b0bc0
