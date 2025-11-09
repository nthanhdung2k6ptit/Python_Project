import pandas as pd

def load_airports(airports_file="data/cleaned/airport_db_cleaned.csv"):
    df = pd.read_csv(airports_file)
    return df

def load_routes(routes_file="data/cleaned/routes_cleaned.csv"):
    df = pd.read_csv(routes_file)
    return df

def get_city_options(airports_df):
    return sorted(airports_df["nameCity"].dropna().unique())

def filter_routes_by_city(routes_df, airports_df, city_from, city_to):
    dep_iatas = airports_df[airports_df["nameCity"] == city_from]["codeIataAirport"].tolist()
    arr_iatas = airports_df[airports_df["nameCity"] == city_to]["codeIataAirport"].tolist()
    filtered = routes_df[
        (routes_df["departureIata"].isin(dep_iatas)) &
        (routes_df["arrivalIata"].isin(arr_iatas))
    ]
    return filtered
