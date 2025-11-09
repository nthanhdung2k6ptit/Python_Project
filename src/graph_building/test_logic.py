import os
from build_graph import build_graph, export_graph_json
from algorithms import shortest_path, shortest_distance, all_paths, graph_metrics, betweenness_centrality

# --- Base project directory ---
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# --- New cleaned CSV paths ---
AIRPORTS_CLEAN = os.path.join(BASE, "data", "cleaned", "airport_db_cleaned.csv")
ROUTES_CLEAN   = os.path.join(BASE, "data", "cleaned", "routes_cleaned.csv")

# --- Export paths ---
EXPORT_FILE_CLEAN = os.path.join(BASE, "data", "graph", "flight_network.json")
EXPORT_FILE_UNKN  = os.path.join(BASE, "data", "graph", "unknow_flight_network.json")

def main():
    # --- Build main flight network ---
    print("Building main flight network...")
    graph_clean = build_graph(AIRPORTS_CLEAN, ROUTES_CLEAN)
    export_graph_json(graph_clean, EXPORT_FILE_CLEAN)
    print("Nodes:", graph_clean.number_of_nodes())
    print("Edges:", graph_clean.number_of_edges())
    print("Metrics:", graph_metrics(graph_clean))
    
    centrality = betweenness_centrality(graph_clean)
    top_hubs = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Top hubs:", top_hubs)   
 

if __name__ == "__main__":
    main()
