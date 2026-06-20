import respx
from httpx import Response

from app.models import RetrievedChunk
from app.retrieval.dense import DenseRetriever
from app.retrieval.ranker import build_nx_graph, graph_distance_matrix, rank_by_graph_distance


def test_build_nx_graph() -> None:
    graph = build_nx_graph([("a", "b", {"type": "rel"}), ("b", "c", {})])
    assert graph.has_edge("a", "b")
    assert graph.has_edge("b", "c")


def test_graph_distance_matrix() -> None:
    graph = build_nx_graph([("a", "b", {}), ("b", "c", {})])
    distances = graph_distance_matrix(graph, {"a"}, {"c"})
    assert distances[("a", "c")] == 2


def test_rank_by_graph_distance() -> None:
    chunks = [
        RetrievedChunk(id="c1", text="one", score=0.5, metadata={}, source="vector"),
        RetrievedChunk(id="c2", text="two", score=0.6, metadata={}, source="vector"),
    ]
    graph_distances = {"c1": 0, "c2": 2}
    ranked = rank_by_graph_distance(chunks, graph_distances, top_k=2)
    assert ranked[0].id == "c1"


@respx.mock
async def test_dense_search() -> None:
    respx.post("http://localhost:11434/api/embeddings").mock(
        return_value=Response(200, json={"embedding": [0.1] * 768})
    )

    retriever = DenseRetriever()
    retriever._client = type(
        "FakeClient",
        (),
        {
            "collection_exists": lambda self, name: True,
            "search": lambda self, **kwargs: [
                type("R", (), {"id": "c1", "score": 0.9, "payload": {"text": "x", "metadata": {}}})()
            ],
        },
    )()

    results = await retriever.search("test", top_k=1)
    assert len(results) == 1
    assert results[0].id == "c1"
