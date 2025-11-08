import os
from build_graph import build_graph, export_graph_json
from algorithms import shortest_path, shortest_distance, all_paths, graph_metrics, betweenness_centrality

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

AIRPORTS = os.path.join(BASE, "data", "cleaned", "airport_db_raw_cleaned.csv")
ROUTES   = os.path.join(BASE, "data", "cleaned", "routes_raw_cleaned.csv")

EXPORT_FILE = os.path.join(BASE, "data", "graph", "flight_network.json")

def main():
    graph = build_graph(AIRPORTS, ROUTES)
    export_graph_json(graph, EXPORT_FILE)

    print("Graph exported:", EXPORT_FILE)
    print("Graph nodes:", graph.number_of_nodes())
    print("Graph edges:", graph.number_of_edges())

    metrics = graph_metrics(graph)
    print("Network metrics:", metrics)

    # top hubs (betweenness)
    centrality = betweenness_centrality(graph)
    top_hubs = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Top hubs:", top_hubs)

    # example queries (guarded)
    try:
        sp = shortest_path(graph, "HAN", "SGN")
        sd = shortest_distance(graph, "HAN", "SGN")
        print("Shortest path HAN -> SGN:", sp)
        print("Shortest distance HAN -> SGN (km):", round(sd, 2))
    except Exception as e:
        print("No HAN->SGN route or error:", e)

    # list up to 20 simple paths with max 3 hops (safe)
    try:
        paths = all_paths(graph, "HAN", "SGN", max_hops=3)
        print("Example paths (<=3 hops):", paths[:20])
    except Exception:
        print("No simple paths HAN->SGN found")

if __name__ == "__main__":
    main()
