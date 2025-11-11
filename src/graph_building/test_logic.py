import os
from build_graph import build_graph, export_graph_json
from algorithms import shortest_path, shortest_distance, all_paths, graph_metrics, betweenness_centrality


# --- Base project directory ---
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# --- Cleaned dataset paths ---
AIRPORTS_WORLD = os.path.join(BASE, "data", "cleaned", "airport_db_cleaned.csv")
ROUTES_WORLD   = os.path.join(BASE, "data", "cleaned", "routes_cleaned.csv")

AIRPORTS_VN = os.path.join(BASE, "data", "cleaned_vn","airport_db_cleaned_vn.csv")
ROUTES_VN   = os.path.join(BASE, "data", "cleaned_vn", "routes_cleaned_vn.csv")

# --- Export path ---
EXPORT_GRAPH = os.path.join(BASE, "data", "graph", "flight_network.json")
EXPORT_GRAPH_VN = os.path.join(BASE, "data", "graph", "flight_netwok_vn.json")

def main():
    print("Building flight network graph...")

    graph_world = build_graph(AIRPORTS_WORLD, ROUTES_WORLD)
    export_graph_json(graph_world, EXPORT_GRAPH)
    graph_vn = build_graph(AIRPORTS_VN, ROUTES_VN)
    export_graph_json(graph_vn, EXPORT_GRAPH_VN)

'''
    # Basic summary
    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())

    # Graph statistics
    print("Metrics:", graph_metrics(graph))

    # Top hub airports by betweenness centrality
    centrality = betweenness_centrality(graph)
    hubs = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Top hubs:", hubs)
'''

if __name__ == "__main__":
    main()
