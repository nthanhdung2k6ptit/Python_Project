import networkx as nx

#hung khec dung file nay bang cach import
def shortest_path(graph, start, end):
    """Return the shortest path by distance between two airports."""
    try:
        return nx.shortest_path(graph, start, end, weight="weight")
    except nx.NetworkXNoPath:
        return None

def shortest_distance(graph, start, end):
    """Return the shortest distance (km) between two airports."""
    try:
        return nx.shortest_path_length(graph, start, end, weight="weight")
    except nx.NetworkXNoPath:
        return float('inf')

def all_paths(graph, start, end, max_hops=None):
    """Return all simple paths, optionally limited by max_hops."""
    try:
        if max_hops is None:
            return list(nx.all_simple_paths(graph, start, end))
        else:
            return list(nx.all_simple_paths(graph, start, end, cutoff=max_hops))
    except nx.NetworkXNoPath:
        return []

def betweenness_centrality(graph):
    """Compute betweenness centrality for all nodes."""
    if len(graph.nodes) == 0:
        return {}
    return nx.betweenness_centrality(graph, weight="weight", normalized=True)

def graph_metrics(graph):
    """Return basic metrics: density, average degree, diameter."""
    if len(graph.nodes) == 0:
        return {"density": 0, "average_degree": 0, "diameter": None}

    density = nx.density(graph)
    degrees = dict(graph.degree())
    avg_degree = sum(degrees.values()) / len(degrees)

    # Handle disconnected graphs safely
    try:
        undirected = graph.to_undirected()
        largest_cc = max(nx.connected_components(undirected), key=len)
        subgraph = undirected.subgraph(largest_cc)
        diameter = nx.diameter(subgraph)
    except Exception:
        diameter = None

    return {
        "density": density,
        "average_degree": avg_degree,
        "diameter": diameter
    }
