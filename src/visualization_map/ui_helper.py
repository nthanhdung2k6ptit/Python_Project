
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


