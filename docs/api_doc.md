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