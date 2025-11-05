import networkx as nx

def shortest_path(graph, start, end):
    return nx.shortest_path(graph, start, end, weight="weight")

def shortest_distance(graph, start, end):
    return nx.shortest_path_length(graph, start, end, weight="weight")

def all_paths(graph, start, end, max_hops=None):
    if max_hops is None:
        return list(nx.all_simple_paths(graph, start, end))
    else:
        return list(nx.all_simple_paths(graph, start, end, cutoff=max_hops))

def betweenness_centrality(graph):
    return nx.betweenness_centrality(graph, weight="weight", normalized=True)

def graph_metrics(graph):
    density = nx.density(graph)
    degrees = dict(graph.degree())
    avg_degree = sum(degrees.values()) / len(degrees)

    undirected = graph.to_undirected()
    largest = max(nx.connected_components(undirected), key=len)
    sub = undirected.subgraph(largest)

    diameter = nx.diameter(sub)

    return {
        "density": density,
        "average_degree": avg_degree,
        "diameter": diameter
    }
