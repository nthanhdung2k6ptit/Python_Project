import os
from build_graph import build_graph, export_graph_pickle
from algorithms import shortest_path, shortest_distance, all_paths, graph_metrics, betweenness_centrality

# Path to project root relative to this file
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AIRPORTS = os.path.join(BASE, "data", "clean", "airport_db_raw_clean.csv")
FLIGHTS = os.path.join(BASE, "data", "clean", "flights_raw_clean.csv")
EXPORT_FILE = os.path.join(BASE, "data", "graph", "flight_network.pkl")

graph = build_graph(AIRPORTS, FLIGHTS)
export_graph_pickle(graph, EXPORT_FILE)
# Example: test two known airport codes
start = "HAN"
end = "SGN"

try:
    route = shortest_path(graph, start, end)
    distance = shortest_distance(graph, start, end)
    print("Route:", route)
    print("Distance (km):", round(distance, 2))

    metrics = graph_metrics(graph)
    print("Network Metrics:", metrics)

    centrality = betweenness_centrality(graph)
    top_hubs = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Top hubs:", top_hubs)

    paths = all_paths(graph, "HAN", "SGN", max_hops=3)
    print("Possible itineraries (max 3 hops):", paths)

except Exception as e:
    print("No route found or error:", e)
