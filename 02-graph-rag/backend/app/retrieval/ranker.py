from typing import Any

import networkx as nx

from app.models import RetrievedChunk


def build_nx_graph(edges: list[tuple[str, str, dict[str, Any]]]) -> nx.Graph:
    """Build an undirected NetworkX graph from a list of (source, target, metadata) edges."""
    graph = nx.Graph()
    for source, target, metadata in edges:
        graph.add_edge(source, target, **metadata)
    return graph


def graph_distance_matrix(
    graph: nx.Graph,
    source_nodes: set[str],
    target_nodes: set[str],
) -> dict[tuple[str, str], int]:
    """Return shortest-path distances between source and target node sets."""
    distances: dict[tuple[str, str], int] = {}
    for source in source_nodes:
        if source not in graph:
            continue
        lengths = nx.single_source_shortest_path_length(graph, source)
        for target in target_nodes:
            if target in lengths:
                distances[(source, target)] = lengths[target]
    return distances


def rank_by_graph_distance(
    vector_results: list[RetrievedChunk],
    graph_distances: dict[str, int],
    top_k: int = 5,
    distance_weight: float = 0.5,
) -> list[RetrievedChunk]:
    """Re-rank vector search results using graph proximity.

    Final score = (1 - distance_weight) * vector_score + distance_weight * graph_score
    where graph_score = 1 / (1 + min_distance). Chunks with no graph connection keep
    only their vector score.
    """
    scored: list[tuple[float, RetrievedChunk]] = []
    for chunk in vector_results:
        distance = graph_distances.get(chunk.id)
        if distance is None:
            combined = chunk.score
        else:
            graph_score = 1.0 / (1.0 + distance)
            combined = (1.0 - distance_weight) * chunk.score + distance_weight * graph_score
        scored.append((combined, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]
