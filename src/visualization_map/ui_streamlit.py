
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))
import streamlit as st
from streamlit_folium import folium_static
from src.visualization_map.map_routes import create_flight_map
from src.visualization_map.ui_helper import load_airports, load_cities
import pandas as pd

st.set_page_config(page_title="🛫 Group 3 | Flight Network", layout="wide")
st.title("🛫 Flight Network - Real Routes Visualization")
df_airports = load_airports()
df_cities = load_cities()

tab1, tab2= st.tabs(['Xem trên map theo sân bay toàn cầu', 'Xem trên map sân bay theo khu vực'])
with tab1:
    st.markdown("Xem các đường bay thực tế trên bản đồ thế giới, xuất phát từ một thành phố cụ thể hoặc toàn cầu.")

    if not df_airports.empty:
        if 'nameCountry' in df_airports.columns and 'country' not in df_airports.columns:
            df_airports = df_airports.rename(columns={'nameCountry': 'country'})
        df_airports['iata_code'] = df_airports['iata_code'].astype(str).str.upper().str.strip()
        iata_country = (df_airports[['iata_code','country']]
                        .dropna(subset=['iata_code'])
                        .drop_duplicates(subset=['iata_code'])
                        .set_index('iata_code')['country']
                        .to_dict())
    else:
        iata_country = {}

    missing_countries = set()
    display_to_iatas = {}
    
    for _, r in df_cities.iterrows():
        city = str(r.get('city_name','')).strip()
        if not city:
            continue
        raw_country = str(r.get('country','') or '').strip()
        iata_field = str(r.get('city_iata','') or '')
        iata_list = [s.strip().upper() for s in iata_field.replace(';',',').split(',') if s.strip()]

        country_full = ""
        for i in iata_list:
            if i in iata_country and iata_country[i]:
                country_full = str(iata_country[i]).strip()
                break

        if not country_full and raw_country:
            country_full = raw_country

        if not country_full:
            missing_countries.add(city)

        display = f"{city} ({country_full})" if country_full else city
        display_to_iatas.setdefault(display, set()).update(iata_list)

    city_map = {k: sorted(v) for k,v in display_to_iatas.items()}
    city_options = [""] + sorted(city_map.keys(), key=lambda s: s.lower())
    st.markdown(
        """
        <style>
        /* giới hạn chiều ngang mặc định cho selectbox */
        .stSelectbox > div { max-width: 520px !important; margin: 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    selected_city = st.selectbox("Chọn thành phố khởi hành (bỏ trống để chọn toàn cầu):", city_options)
    
    selected_iatas = city_map.get(selected_city, []) if selected_city else []

    if st.button("Hiển thị đường bay"):
        st.info(f"Đang hiển thị các đường bay xuất phát từ thành phố {selected_city or 'trên TOÀN CẦU'} ...")
        m = create_flight_map(departure_city_iatas = selected_iatas) 
        col_left, col_center, col_right = st.columns([1,6,1])
        with col_center:
            folium_static(m, width=800, height=600)
        st.success("Đã hiển thị bản đồ thành công <3")
        
with tab2:
    st.markdown("Xem các đường bay thực tế trên bản đồ thế giới, khởi hành từ một thành phố trong vùng được chọn.")

    airports_df = df_airports.copy()
    airports_df['iata_code'] = airports_df['iata_code'].astype(str).str.upper().str.strip()
    countries = sorted(airports_df['country'].dropna().unique().tolist())
    chosen_countries = st.multiselect("Chọn quốc gia để mô phỏng khu vực:", countries, default=[])
    
    airports_region = airports_df[airports_df['country'].isin(chosen_countries)].copy() if chosen_countries else airports_df.copy()
    region_iatas_set = set(airports_region['iata_code'].astype(str).str.upper().dropna().unique())

    st.markdown("<div style='max-width:520px;margin:0 auto;'>", unsafe_allow_html=True)
    region_city_map = {}
    for _, r in df_cities.iterrows():
        city = str(r.get('city_name','')).strip()
        if not city:
            continue
        iata_field = str(r.get('city_iata','') or '')
        iata_list = [s.strip().upper() for s in iata_field.replace(';',',').split(',') if s.strip()]
        valid = [i for i in iata_list if i in region_iatas_set]
        if not valid:
            continue
        display = f"{city} ({r.get('country','')})" if r.get('country') else city
        region_city_map.setdefault(display, set()).update(valid)
    region_city_map = {k: sorted(v) for k,v in region_city_map.items()}
    region_city_options = [""] + sorted(region_city_map.keys(), key=lambda s: s.lower())

    sel_city_reg = st.selectbox("Chọn thành phố khởi hành trong vùng đã chọn:", region_city_options)
    st.markdown("</div>", unsafe_allow_html=True)

    sel_iatas_reg = region_city_map.get(sel_city_reg, []) if sel_city_reg else []

    if st.button("Hiển thị đường bay (khu vực)"):
        if not region_iatas_set and not sel_iatas_reg:
            st.warning("Chưa chọn khu vực hoặc khu vực không có sân bay trong dữ liệu.")
        else:
            status = st.info("Đang nạp dữ liệu khu vực...")
            arrivals_valid = set()
            if sel_iatas_reg:
                routes_path = project_root / "data" / "cleaned" / "routes_cleaned.csv"
                if routes_path.exists():
                    try:
                        df_routes = pd.read_csv(routes_path, usecols=['departure_iata','arrival_iata'])
                        df_routes['departure_iata'] = df_routes['departure_iata'].astype(str).str.upper().str.strip()
                        df_routes['arrival_iata'] = df_routes['arrival_iata'].astype(str).str.upper().str.strip()
                        arrivals_from_selected = set(df_routes[df_routes['departure_iata'].isin([s.upper() for s in sel_iatas_reg])]['arrival_iata'].unique())
                        
                        arrivals_valid = {a for a in arrivals_from_selected if a in set(df_airports['iata_code'].astype(str).str.upper())}
                    except Exception as e:
                        st.error("Không đọc được routes file để tìm điểm đến; sẽ chỉ hiện sân bay trong khu vực đã chọn.")
                else:
                    st.caption("Không tìm thấy routes_cleaned.csv — sẽ chỉ hiện sân bay trong khu vực đã chọn.")

            allowed_iatas = set(region_iatas_set)
            allowed_iatas.update(arrivals_valid)
            allowed_iatas.update([s.upper() for s in sel_iatas_reg])

            status.text(f"Đang tải bản đồ với {len(allowed_iatas)} sân bay (trong đó {len(sel_iatas_reg)} là sân bay khởi hành đã chọn).")
            try:
                m = create_flight_map(departure_city_iatas=sel_iatas_reg, allowed_iatas=allowed_iatas)
            except Exception as e:
                st.error("Tạo bản đồ khu vực không thành công.")
                st.exception(e)
            else:
                c1, c2, c3 = st.columns([1,6,1])
                with c2:
                    folium_static(m, width=900, height=650)
                st.success("Đã tải xong bản đồ khu vực được chọn, có thể xem ngay bây giờ <3.")
    