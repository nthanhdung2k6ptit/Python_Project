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
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def build_graph(airport_csv, flight_csv):
    airports = pd.read_csv(airport_csv)
    flights = pd.read_csv(flight_csv)

    # Select columns we need
    airports = airports[[
        "codeiataairport", "latitudeairport", "longitudeairport"
    ]].dropna()

    flights = flights[[
        "departureiata", "arrivaliata",
        "airlineiata", "flightnumber"
    ]].dropna()

    # Index airports by IATA code
    airports = airports.set_index("codeiataairport")

    # Create graph
    G = nx.DiGraph()

    # --- ADD ALL AIRPORTS AS NODES FIRST ---
    for code, row in airports.iterrows():
        G.add_node(code, 
                   latitude=float(row["latitudeairport"]), 
                   longitude=float(row["longitudeairport"]))

    # --- ADD FLIGHT ROUTES AS EDGES ---
    for _, row in flights.iterrows():
        dep = row["departureiata"]
        arr = row["arrivaliata"]

        if dep in airports.index and arr in airports.index:
            lat1, lon1 = airports.loc[dep][["latitudeairport", "longitudeairport"]]
            lat2, lon2 = airports.loc[arr][["latitudeairport", "longitudeairport"]]
            dist = haversine(lat1, lon1, lat2, lon2)

            G.add_edge(dep, arr,
                       weight=dist,
                       airline=row["airlineiata"],
                       flight=row["flightnumber"])

    return G

def export_graph_json(graph, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data = json_graph.node_link_data(graph)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Graph exported as JSON: {filename}")
