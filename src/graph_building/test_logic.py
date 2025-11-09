import os
from build_graph import build_graph, export_graph_json
from algorithms import shortest_path, shortest_distance, all_paths, graph_metrics, betweenness_centrality

# --- Base project directory ---
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# --- Cleaned CSV paths ---
AIRPORTS_CLEAN = os.path.join(BASE, "data", "cleaned", "airport_db_cleaned.csv")
FLIGHTS_CLEAN  = os.path.join(BASE, "data", "cleaned", "flight_tracker_cleaned.csv")

FLIGHTS_UNKN = os.path.join(BASE, "data", "cleaned", "unknow_flight_tracker_cleaned.csv")

# --- Export path ---
EXPORT_FILE_CLEAN = os.path.join(BASE, "data", "graph", "flight_network.json")
EXPORT_FILE_UNKN = os.path.join(BASE, "data", "graph", "flight_network_unknow.json")

def main():
    print("Building flight network from airport + real-time flight tracker...")
    
    graph_clean = build_graph(AIRPORTS_CLEAN, FLIGHTS_CLEAN)
    export_graph_json(graph_clean, EXPORT_FILE_CLEAN)
    
    graph_unknow = build_graph(AIRPORTS_CLEAN, FLIGHTS_UNKN)
    export_graph_json(graph_unknow, EXPORT_FILE_UNKN)
    '''
    print("Nodes:", graph_clean.number_of_nodes())
    print("Edges:", graph_clean.number_of_edges())
    
    print("Metrics:", graph_metrics(graph_clean))
    
    centrality = betweenness_centrality(graph_clean)
    top_hubs = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Top hubs:", top_hubs)
    '''

if __name__ == "__main__":
    main()
