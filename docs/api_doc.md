Ghi chú về API
DANH SÁCH ĐẦY ĐỦ APIs CỦA GÓI DEVELOPER

1. FLIGHT TRACKER API
Mô tả: Theo dõi vị trí máy bay real-time trên toàn thế giới
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

2. REAL-TIME SCHEDULES API
Mô tả: Lịch bay đến/đi của sân bay HIỆN TẠI
Dữ liệu:

Trạng thái: active, scheduled, landed, cancelled, incident, diverted
Sân bay (IATA, ICAO)
Terminal & Gate
Giờ dự kiến/thực tế khởi hành/hạ cánh
Delay (nếu có)
Thông tin hãng bay
Số hiệu chuyến bay

Use case: Airport departure/arrival boards, booking platforms

3. HISTORICAL SCHEDULES API
Mô tả: Lịch sử lịch bay của sân bay (dữ liệu quá khứ)
Dữ liệu:

Lịch sử trạng thái: landed, cancelled, delayed, unknown
Thời gian thực tế vs dự kiến
Số phút delay
Terminal & Gate lịch sử
Lọc theo date range (tối đa 30 ngày/lần)

Use case: Flight delay claims, performance analysis, statistics

4. FUTURE SCHEDULES API
Mô tả: Lịch bay TƯƠNG LAI của sân bay
Dữ liệu:

Lịch bay các ngày sắp tới
Giờ khởi hành/hạ cánh dự kiến
Terminal & Gate thường dùng
Thông tin máy bay
Thứ trong tuần
Hãng bay

Use case: Travel planning, booking engines, schedule checkers

5. AIRLINE ROUTES API
Mô tả: Tất cả tuyến bay của các hãng hàng không
Dữ liệu:

Sân bay đi/đến (IATA, ICAO)
Terminal
Thời gian bay
Hãng bay vận hành
Số hiệu chuyến bay
Số đăng ký máy bay

Use case: Route analysis, competitor research, network planning

6. NEARBY AIRPORTS API
Mô tả: Tìm sân bay/thành phố gần tọa độ GPS
Dữ liệu:

Loại địa điểm: airport, railway, bus station, heliport, seaport
IATA, ICAO codes
Tên sân bay/thành phố
Tọa độ (lat, lng)
Khoảng cách từ điểm tìm kiếm
Quốc gia

Use case: Alternative airports, travel apps, location-based services

7. AUTOCOMPLETE API
Mô tả: Gợi ý tìm kiếm sân bay/thành phố khi gõ
Dữ liệu:

Loại: city, airport, railway, heliport...
IATA, ICAO codes
Tên đầy đủ
Thành phố, quốc gia
Tọa độ
Timezone

Use case: Search boxes, booking forms, user input assistance

8. SATELLITE TRACKER API
Mô tả: Theo dõi vệ tinh quỹ đạo Trái Đất real-time
Dữ liệu:

NORAD ID
Tên vệ tinh
Quốc gia sở hữu
Ngày phóng
Vị trí hiện tại (lat, lng, altitude)
Tọa độ ECI (Earth-centered inertial)
Thông số quỹ đạo (apogee, perigee, inclination, period)
Right ascension
TLE (Two-line Element Set)
Kích thước vệ tinh

Use case: Space tracking apps, education, satellite monitoring

9. AIRLINES DATABASE API
Mô tả: Database đầy đủ tất cả hãng bay thế giới
Dữ liệu:

Tên hãng bay
IATA, ICAO codes
IATA prefix, accounting code
Hub airport
Quốc gia (name, ISO code)
Trạng thái (active, closed...)
Loại hãng bay
Năm thành lập
Số lượng máy bay
Độ tuổi trung bình đội bay
Website, social media, phone

Use case: Reference data, airline info lookups

10. AIRPORTS DATABASE API
Mô tả: Database tất cả sân bay, helipad, seaport thế giới
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

11. AIRCRAFT DATABASE API
Mô tả: Database tất cả loại máy bay
Dữ liệu:

Tên, model máy bay
Số đăng ký (registration number)
IATA typecode, ICAO24 hex code
Ngày rollout, first flight, delivery, registration
Construction number, production line, series
Chủ sở hữu, hãng bay vận hành
Số hạng ghế (class, seats)
Số động cơ
Tuổi máy bay
Trạng thái

Use case: Aircraft identification, fleet tracking

12. CITY DATABASE API
Mô tả: Database tất cả thành phố có liên quan hàng không
Dữ liệu:

Tên thành phố
IATA code
Quốc gia (ISO-2)
Tọa độ (lat, lng)
Timezone, GMT offset
Geoname ID
Tên dịch

Use case: City lookups, travel planning

13. COUNTRY DATABASE API
Mô tả: Database tất cả quốc gia và vùng lãnh thổ
Dữ liệu:

Tên quốc gia
Tên dịch
IATA, ISO-2, ISO-3, Numeric codes
Tiền tệ (tên, code)
Châu lục
Thủ đô
Các nước láng giềng
Mã điện thoại
Độ phổ biến
Ngôn ngữ sử dụng

Use case: Country lookups, international apps

14. TAXES DATABASE API
Mô tả: Database IATA tax codes (thuế/phí hàng không)
Dữ liệu:

Tax ID nội bộ
Tên loại thuế/phí
IATA tax code chính thức

Use case: Pricing systems, booking platforms

15. "8 OTHER API SYSTEMS"
Theo mô tả gói, còn có 8 API systems khác không được liệt kê chi tiết, có thể bao gồm:

Flight Delay API (riêng biệt)
Airport Tax API
Weather API (nếu có)
Các API bổ sung khác


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

3. HISTORICAL SCHEDULES API
Endpoint: http://aviation-edge.com/v2/public/flightsHistory
Parameters:

key - API key (required)
iataCode - IATA code sân bay (required)
type - "departure" hoặc "arrival" (required)
date_from - Ngày bắt đầu YYYY-MM-DD (required)
date_to - Ngày kết thúc YYYY-MM-DD (required, max 30 days range)
status - Lọc theo trạng thái (optional): cancelled, delayed, landed

Example:
http://aviation-edge.com/v2/public/flightsHistory?key=YOUR_KEY&iataCode=HAN&type=departure&date_from=2025-10-01&date_to=2025-10-31
http://aviation-edge.com/v2/public/flightsHistory?key=YOUR_KEY&iataCode=SGN&type=arrival&date_from=2025-10-01&date_to=2025-10-15&status=delayed

3B. FLIGHT HISTORY API (Alternative)
Endpoint: http://aviation-edge.com/v2/public/flightHistory
Parameters:

key - API key (required)
code - Flight code hoặc Airport code (required)
type - "flight" hoặc "airport" (required)
date_from - Ngày bắt đầu YYYY-MM-DD (required)
date_to - Ngày kết thúc YYYY-MM-DD (required)

Example:
http://aviation-edge.com/v2/public/flightHistory?key=YOUR_KEY&code=VN123&type=flight&date_from=2025-10-01&date_to=2025-10-31
http://aviation-edge.com/v2/public/flightHistory?key=YOUR_KEY&code=HAN&type=airport&date_from=2025-10-01&date_to=2025-10-31

4. FUTURE SCHEDULES API
Endpoint: http://aviation-edge.com/v2/public/futureTimetable
Parameters:

key - API key (required)
iataCode - IATA code sân bay (required)
type - "departure" hoặc "arrival" (required)
date - Ngày trong tương lai YYYY-MM-DD (required)

Example:
http://aviation-edge.com/v2/public/futureTimetable?key=YOUR_KEY&iataCode=HAN&type=departure&date=2025-12-25
http://aviation-edge.com/v2/public/futureTimetable?key=YOUR_KEY&iataCode=SGN&type=arrival&date=2025-11-10

5. AIRLINE ROUTES API
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

6. NEARBY AIRPORTS API
Endpoint: http://aviation-edge.com/v2/public/nearby
Parameters:

key - API key (required)
lat - Latitude (required)
lng - Longitude (required)
distance - Khoảng cách tối đa (km) (optional, default: 50)

Example:
http://aviation-edge.com/v2/public/nearby?key=YOUR_KEY&lat=21.0285&lng=105.8542&distance=100
http://aviation-edge.com/v2/public/nearby?key=YOUR_KEY&lat=10.8231&lng=106.6297&distance=50

7. AUTOCOMPLETE API
Endpoint: http://aviation-edge.com/v2/public/autocomplete
Parameters:

key - API key (required)
name - Từ khóa tìm kiếm (required, min 2 ký tự)

Example:
http://aviation-edge.com/v2/public/autocomplete?key=YOUR_KEY&name=han
http://aviation-edge.com/v2/public/autocomplete?key=YOUR_KEY&name=saigon
http://aviation-edge.com/v2/public/autocomplete?key=YOUR_KEY&name=JFK

8. SATELLITE TRACKER API
Endpoint: http://aviation-edge.com/v2/public/satellites
Parameters:

key - API key (required)
limit - Giới hạn số kết quả (optional)
noradId - NORAD ID của vệ tinh cụ thể (optional)

Example:
http://aviation-edge.com/v2/public/satellites?key=YOUR_KEY&limit=100
http://aviation-edge.com/v2/public/satellites?key=YOUR_KEY&noradId=25544
(25544 = ISS - International Space Station)

9. AIRLINES DATABASE API
Endpoint: http://aviation-edge.com/v2/public/airlineDatabase
Parameters:

key - API key (required)
codeIataAirline - IATA code hãng bay (optional)
codeIcaoAirline - ICAO code hãng bay (optional)
codeIso2Country - ISO-2 country code (optional)
nameAirline - Tên hãng bay (optional)

Example:
http://aviation-edge.com/v2/public/airlineDatabase?key=YOUR_KEY
http://aviation-edge.com/v2/public/airlineDatabase?key=YOUR_KEY&codeIataAirline=VN
http://aviation-edge.com/v2/public/airlineDatabase?key=YOUR_KEY&codeIso2Country=VN

10. AIRPORTS DATABASE API
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

11. AIRCRAFT DATABASE API
Endpoint: http://aviation-edge.com/v2/public/aircraftDatabase
Parameters:

key - API key (required)
numberRegistration - Số đăng ký máy bay (optional) (VD: VN-A861)
hexIcaoAircraft - ICAO24 hex code (optional)
codeIataAirline - IATA code hãng bay (optional)

Example:
http://aviation-edge.com/v2/public/aircraftDatabase?key=YOUR_KEY
http://aviation-edge.com/v2/public/aircraftDatabase?key=YOUR_KEY&numberRegistration=VN-A861
http://aviation-edge.com/v2/public/aircraftDatabase?key=YOUR_KEY&codeIataAirline=VN

12. CITY DATABASE API
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

13. COUNTRY DATABASE API
Endpoint: http://aviation-edge.com/v2/public/countryDatabase
Parameters:

key - API key (required)
codeIso2Country - ISO-2 country code (optional)
codeIso3Country - ISO-3 country code (optional)
nameCountry - Tên quốc gia (optional)

Example:
http://aviation-edge.com/v2/public/countryDatabase?key=YOUR_KEY
http://aviation-edge.com/v2/public/countryDatabase?key=YOUR_KEY&codeIso2Country=VN
http://aviation-edge.com/v2/public/countryDatabase?key=YOUR_KEY&codeIso3Country=VNM

14. TAXES DATABASE API
Endpoint: http://aviation-edge.com/v2/public/taxDatabase
Parameters:

key - API key (required)
codeIataTax - IATA tax code (optional)

Example:
http://aviation-edge.com/v2/public/taxDatabase?key=YOUR_KEY
http://aviation-edge.com/v2/public/taxDatabase?key=YOUR_KEY&codeIataTax=YQ
<<<<<<< HEAD
=======

>>>>>>> 75dc2c8c4b76fcf1c24162057ddebfeefbe899d7
