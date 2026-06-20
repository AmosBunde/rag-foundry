"""End-to-end integration test of the Graph RAG backend using mocked stores.

This test exercises the full request path (auth -> ingest -> graph query ->
graph endpoints) without requiring live Neo4j or Qdrant instances.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import RetrievedChunk


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def token(client: TestClient) -> str:
    response = client.post("/api/v1/auth/token", data={"username": "demo", "password": "demo"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_end_to_end_ingest_and_query(client: TestClient, token: str) -> None:
    """Ingest a document and run a graph query through the public API."""
    vector_results = [
        RetrievedChunk(
            id="doc-001::chunk::0",
            text="Graph RAG uses Neo4j.",
            score=0.95,
            metadata={"parent_id": "doc-001", "chunk_index": 0},
            source="vector",
        )
    ]

    with (
        patch("app.ingestion.IngestionService.ingest", new=AsyncMock(
            return_value={
                "indexed": 1,
                "entities_created": 2,
                "relationships_created": 1,
                "errors": [],
            }
        )),
        patch("app.routers.query.DenseRetriever") as MockDense,
        patch("app.routers.query.GraphRepository") as MockGraph,
        patch("app.routers.query.extract_entities") as MockExtract,
    ):
        MockDense.return_value.search = AsyncMock(return_value=vector_results)
        MockGraph.return_value.get_chunk_ids_near_entities = AsyncMock(return_value={"doc-001::chunk::0": 0})
        MockExtract.return_value = [{"id": "entity:neo4j"}]

        ingest_response = client.post(
            "/api/v1/ingest",
            json={
                "documents": [
                    {
                        "id": "doc-001",
                        "text": "Graph RAG uses Neo4j and Qdrant.",
                        "metadata": {"source": "integration-test"},
                    }
                ]
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert ingest_response.status_code == 200

        query_response = client.post(
            "/api/v1/query/graph",
            json={"query": "Neo4j graph", "top_k": 3, "graph_depth": 2},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert query_response.status_code == 200
    data = query_response.json()
    assert data["query"] == "Neo4j graph"
    assert len(data["results"]) <= 3


def test_graph_entities_and_expand(client: TestClient, token: str) -> None:
    """List entities and expand a selected entity."""
    with patch("app.routers.graph.GraphRepository") as MockGraph:
        MockGraph.return_value.get_entities = AsyncMock(
            return_value=[{"id": "entity:neo4j", "name": "Neo4j", "label": "Database"}]
        )
        MockGraph.return_value.expand_entity = AsyncMock(
            return_value={
                "id": "entity:neo4j",
                "name": "Neo4j",
                "label": "Database",
                "related": [{"id": "entity:graph", "name": "Graph", "label": "Concept"}],
            }
        )
        MockGraph.return_value.get_chunks_by_ids = AsyncMock(return_value=[])

        entities_response = client.get(
            "/api/v1/graph/entities",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert entities_response.status_code == 200
        entities = entities_response.json()
        assert len(entities) == 1

        expand_response = client.get(
            "/api/v1/graph/expand/entity:neo4j",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert expand_response.status_code == 200
        data = expand_response.json()
        assert data["entity"]["id"] == "entity:neo4j"
        assert len(data["related_entities"]) == 1
