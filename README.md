# ✈️ Graph Network Project ✈️

### Team PTIT - @2025

##  Mục tiêu
Mô phỏng và phân tích mạng lưới chuyến bay toàn cầu bằng Python, kết hợp dữ liệu từ **Aviation Edge API**.

##  Cấu trúc Project

dung ngu # Group 3
# Cài git vào máy: 
https://git-scm.com/install/windows


# Lấy folder về máy lần đầu: (chỉ cần lấy duy nhất 1 lần)
git clone https://github.com/nthanhdung2k6ptit/Graph_Network_Project.git

# Những lần sau chỉ cần làm các bước sau nha mng:
1. git pull origin main     # Lấy code mới nhất từ GitHub về máy
    Khi code xong nên pull lại 1 lần nữa để đồng bộ code của cả nhóm (làm lại bước 1)
2. git add .                # Thêm file bạn vừa sửa / cập nhật code vừa mình làm
3. git commit -m "Cập nhật phần API của Thành viên 1|2|3..."
4. git push origin main     # Đẩy code lên GitHub
=> Nghĩa là:

pull trước để không đè code người khác

push sau khi commit xong


_____________________________________________________________
#  Graph Network – Aviation Edge API Project

##  Team Members
1. API Connection – TV1 - Nguyễn Thị Phương Anh
2. Data Cleaning – TV2 - Nguyễn Thị Ngọc Lan
3. Graph Building – TV3 - Đỗ Minh Đức
4. Graph Visualization – TV4 - Vũ Công Duy Hưng
5. Map UI – TV5 - Nguyễn Thành Dũng
6. Data Analysis – TV6 - Nguyễn Hữu Trung

##  Tech Stack
Python 3.x | requests | pandas | numpy | networkx | matplotlib | plotly | folium | seaborn | streamlit

##  Project Flow
TV1 → TV2 → TV3 → (TV4, TV5, TV6)

##  How to run
```bash
pip install -r requirements.txt
python src/main.py
--
python src/main.py
streamlit run src/visualization_map/ui_streamlit.py

-------------------------------------------------------------
Các ký hiệu Git trong VS Code:

U (xanh) = Untracked - file mới chưa add
M (cam) = Modified - file đã sửa đổi
A (xanh lá) = Added - file mới đã add vào staging
D (đỏ) = Deleted - file đã xóa
C = Conflict - xung đột khi merge
R = Renamed - file đổi tên


--------------------------------------------------------------
Ctrl+Shift+P
## Tạo VENV
py -m venv .venv

## Kích hoạt
    ### PowerShell
    .\.venv\Scripts\Activate.ps1
    ### CMD
    .\.venv\Scripts\activate.bat

## Thoát venv
deactivate
