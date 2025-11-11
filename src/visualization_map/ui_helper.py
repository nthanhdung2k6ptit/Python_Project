# Gộp 2 file airports cho dropdown chọn thành phố và lọc routes

import pandas as pd
import os

def load_airports(base_path='data/cleaned'):
    '''
    Load và gộp data sân bay toàn cầu và Việt Nam
    Trả về DataFrame sân bay
    '''
    path_global = os.path.join(base_path, "airport_db_cleaned.csv")
    path_vn = os.path.join(base_path + "_vn", "airport_db_cleaned_vn.csv")

    df_g = pd.read_csv(path_global)
    df_v = pd.read_csv(path_vn)

    df = pd.concat([df_g, df_v]).drop_duplicates(subset=['iata_code'])
    return df[['iata_code', 'airport_name', 'country']].dropna(subset=['iata_code'])

# New: load city db (global + VN), normalize basic columns
def load_cities(base_path='data/cleaned'):
    '''
    Load và gộp data thành phố toàn cầu và Việt Nam
    Trả về DataFrame với cột 'city_name' và 'city_iata' (nếu có)
    '''
    path_global = os.path.join(base_path, "city_db_cleaned.csv")
    path_vn = os.path.join(base_path + "_vn", "city_db_cleaned_vn.csv")

    dfs = []
    if os.path.exists(path_global):
        dfs.append(pd.read_csv(path_global))
    if os.path.exists(path_vn):
        dfs.append(pd.read_csv(path_vn))

    if not dfs:
        return pd.DataFrame(columns=['city_name', 'city_iata'])

    df = pd.concat(dfs, ignore_index=True).drop_duplicates()

    # pick city name column (accept various names)
    for cname in ['city_name', 'city', 'name', 'name_city', 'cityName']:
        if cname in df.columns:
            df['city_name'] = df[cname].astype(str)
            break

    # pick city iata column (accept various names that appear in your CSVs)
    for icol in ['city_iata', 'code_iata_city', 'iata_code', 'iata', 'iata_city', 'iata_codes']:
        if icol in df.columns:
            # keep original formatting but convert NaN to empty string
            df['city_iata'] = df[icol].fillna("").astype(str)
            break

    # ensure both columns exist
    if 'city_name' not in df.columns:
        df['city_name'] = ""
    if 'city_iata' not in df.columns:
        df['city_iata'] = ""

    return df[['city_name', 'city_iata']].dropna(subset=['city_name'])


