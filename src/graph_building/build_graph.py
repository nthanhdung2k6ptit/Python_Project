import pandas as pd
import networkx as nx
import json

def build_graph(airports_file, routes_file):
    # Load datasets
    airports = pd.read_csv(airports_file)
    routes = pd.read_csv(routes_file)

    # Keep only required columns
    airports = airports[["iata_code", "airport_name", "country", "latitude", "longitude"]]
    routes = routes[["departure_iata", "arrival_iata", "airline_iata", "flight_number"]]

    # Drop rows with missing key info
    airports = airports.dropna(subset=["iata_code"])
    routes = routes.dropna(subset=["departure_iata", "arrival_iata"])

    # Create graph (directed)
    G = nx.DiGraph()

    # Add airport nodes
    for _, row in airports.iterrows():
        G.add_node(
            row["iata_code"],
            name=row["airport_name"],
            country=row["country"],
            lat=float(row["latitude"]),
            lon=float(row["longitude"])
        )

    # Add route edges
    for _, row in routes.iterrows():
        dep = row["departure_iata"]
        arr = row["arrival_iata"]

        if dep in G.nodes and arr in G.nodes:  # Only add valid connections
            G.add_edge(
                dep, arr,
                airline=row["airline_iata"],
                flight=row["flight_number"]
            )

    return G


def export_graph_json(G, output_file):
    """ Convert graph to JSON and save. """
    data = nx.node_link_data(G)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
