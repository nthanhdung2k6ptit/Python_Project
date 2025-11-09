import pandas as pd
import numpy as np
import networkx as nx
import os
import json
from networkx.readwrite import json_graph

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth (in km).
    """
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def build_graph(airport_csv, flight_csv):
    """
    Build a directed graph of airports and flights.
    Nodes = airports
    Edges = direct flights
    """
    # --- LOAD AIRPORT DATA ---
    airports = pd.read_csv(airport_csv)
    airports = airports[[
        "iata_code", "latitude", "longitude", "airport_name", "country"
    ]].dropna(subset=["iata_code"])
    airports = airports.set_index("iata_code")

    # --- LOAD FLIGHT DATA ---
    flights = pd.read_csv(flight_csv)
    flights = flights[[
        "departure_iata", "arrival_iata", "airline_iata", "flight_number"
    ]].dropna()

    # --- CREATE GRAPH ---
    G = nx.DiGraph()

    # Add airport nodes
    for code, row in airports.iterrows():
        G.add_node(code,
                   latitude=float(row["latitude"]),
                   longitude=float(row["longitude"]),
                   name=row["airport_name"],
                   country=row["country"])

    # Add flight edges
    for _, row in flights.iterrows():
        dep = row["departure_iata"]
        arr = row["arrival_iata"]

        if dep in airports.index and arr in airports.index:
            lat1, lon1 = airports.loc[dep][["latitude", "longitude"]]
            lat2, lon2 = airports.loc[arr][["latitude", "longitude"]]
            dist = haversine(lat1, lon1, lat2, lon2)

            G.add_edge(dep, arr,
                       weight=dist,
                       airline=row["airline_iata"],
                       flight=row["flight_number"])
    return G

def export_graph_json(graph, filename):
    """
    Export the graph to a JSON file.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data = json_graph.node_link_data(graph)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Graph exported as JSON: {filename}")
