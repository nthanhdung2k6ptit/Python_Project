import os
from build_graph import build_graph, export_graph_json
from algorithms import shortest_path, shortest_distance, all_paths, graph_metrics, betweenness_centrality


# --- Base project directory ---
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# --- Cleaned dataset paths ---
AIRPORTS_CLEAN = os.path.join(BASE, "data", "cleaned", "airport_db_cleaned.csv")
ROUTES_CLEAN   = os.path.join(BASE, "data", "cleaned", "routes_cleaned.csv")

# --- Export path ---
EXPORT_GRAPH = os.path.join(BASE, "data", "graph", "flight_network.json")


def main():
    print("Building flight network graph...")

    # Build graph based on cleaned and aligned data
    graph = build_graph(AIRPORTS_CLEAN, ROUTES_CLEAN)

    # Export graph to JSON
    export_graph_json(graph, EXPORT_GRAPH)

    # Basic summary
    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())

    # Graph statistics
    print("Metrics:", graph_metrics(graph))

    # Top hub airports by betweenness centrality
    centrality = betweenness_centrality(graph)
    hubs = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Top hubs:", hubs)


if __name__ == "__main__":
    main()
