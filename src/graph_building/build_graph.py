import pandas as pd
import numpy as np
import networkx as nx
import os
import pickle

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def build_graph(airport_csv, flight_csv):
    airports = pd.read_csv(airport_csv)
    flights = pd.read_csv(flight_csv)

    airports = airports[[
        "codeiataairport", "latitudeairport", "longitudeairport"
    ]].dropna()

    flights = flights[[
        "departure_iatacode", "arrival_iatacode",
        "airline_iatacode", "flight_number"
    ]].dropna()

    airports = airports.set_index("codeiataairport")

    G = nx.DiGraph()

    for idx, row in flights.iterrows():
        dep = row["departure_iatacode"]
        arr = row["arrival_iatacode"]
        if dep in airports.index and arr in airports.index:
            lat1, lon1 = airports.loc[dep][["latitudeairport", "longitudeairport"]]
            lat2, lon2 = airports.loc[arr][["latitudeairport", "longitudeairport"]]
            dist = haversine(lat1, lon1, lat2, lon2)
            G.add_edge(dep, arr,
                       weight=dist,
                       airline=row["airline_iatacode"],
                       flight=row["flight_number"])
    return G

def export_graph_pickle(graph, filename):
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        pickle.dump(graph, f)
    print(f"Graph exported as Pickle: {filename}")