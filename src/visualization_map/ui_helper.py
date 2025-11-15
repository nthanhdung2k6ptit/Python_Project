# Gộp 2 file airports cho dropdown chọn thành phố và lọc routes

import pandas as pd
import os

def load_airports(base_path='data/cleaned'):

    path_global = os.path.join(base_path, "airport_db_cleaned.csv")
    path_vn = os.path.join(base_path + "_vn", "airport_db_cleaned_vn.csv")

    df_g = pd.read_csv(path_global)
    df_v = pd.read_csv(path_vn)

    df = pd.concat([df_g, df_v]).drop_duplicates(subset=['iata_code'])
    return df[['iata_code', 'airport_name', 'country']].dropna(subset=['iata_code'])

def load_cities(base_path='data/cleaned'):
    path_global = os.path.join(base_path, "city_db_cleaned.csv")
    path_vn = os.path.join(base_path + "_vn", "city_db_cleaned_vn.csv")
    dfs = []
    if os.path.exists(path_global):
        dfs.append(pd.read_csv(path_global))
    if os.path.exists(path_vn):
        dfs.append(pd.read_csv(path_vn))
    if not dfs:
        return pd.DataFrame(columns=['city_name', 'city_iata', 'country'])
    df = pd.concat(dfs, ignore_index=True).drop_duplicates()

    for cname in ['name_city', 'city_name', 'city', 'name']:
        if cname in df.columns:
            df['city_name'] = df[cname].astype(str)
            break
    if 'city_name' not in df.columns:
        df['city_name'] = ""
        

    for icol in ['code_iata_city', 'city_iata', 'iata_codes', 'iata', 'iata_code']:
        if icol in df.columns:
            df['city_iata'] = df[icol].fillna("").astype(str)
            break
    if 'city_iata' not in df.columns:
        df['city_iata'] = ""

    country_col = None
    for ccol in ['code_iso2_country', 'code_iso2', 'country', 'country_name', 'name_country', 'codeIso2Country']:
        if ccol in df.columns:
            country_col = ccol
            break
    if country_col:
        df['country'] = df[country_col].astype(str).fillna("").str.strip()
    else:
        df['country'] = ""
        
    df['country'] = df['country'].replace({"nan": ""})
    df.loc[df['country'].str.upper() == 'VN', 'country'] = 'Vietnam'

    return df[['city_name', 'city_iata', 'country']].dropna(subset=['city_name'])


