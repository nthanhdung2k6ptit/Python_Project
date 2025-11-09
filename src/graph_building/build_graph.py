import pandas as pd
import numpy as np
import networkx as nx
import os
import json
from networkx.readwrite import json_graph

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def build_graph(airport_csv, flight_csv):
    airports = pd.read_csv(airport_csv)
    flights = pd.read_csv(flight_csv)

    # Normalize column names → lowercase
    airports.columns = airports.columns.str.lower()
    flights.columns = flights.columns.str.lower()

    # Required airport fields:
    # iata_code, latitude, longitude
    airports = airports[["iata_code", "latitude", "longitude"]].dropna()
    airports = airports.rename(columns={
        "iata_code": "iata",
        "latitude": "lat",
        "longitude": "lon"
    })
    airports = airports.set_index("iata")

    # Required flight fields:
    flights = flights[["departure_iata_code", "arrival_iata_code", "airline_iata_code", "flight_iata_number"]].dropna()
    flights = flights.rename(columns={
        "departure_iata_code": "dep",
        "arrival_iata_code": "arr",
        "airline_iata_code": "airline",
        "flight_iata_number": "flight"
    })

    G = nx.DiGraph()

    # Add airports as nodes
    for code, row in airports.iterrows():
        G.add_node(code,
                   latitude=float(row["lat"]),
                   longitude=float(row["lon"]))

    # Add flights as directed edges
    for _, row in flights.iterrows():
        dep = row["dep"]
        arr = row["arr"]

        if dep in airports.index and arr in airports.index:
            lat1, lon1 = airports.loc[dep][["lat", "lon"]]
            lat2, lon2 = airports.loc[arr][["lat", "lon"]]
            dist = haversine(lat1, lon1, lat2, lon2)

            G.add_edge(dep, arr,
                       weight=dist,
                       airline=row["airline"],
                       flight=row["flight"])

    return G

def export_graph_json(graph, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data = json_graph.node_link_data(graph)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Graph exported as JSON: {filename}")
