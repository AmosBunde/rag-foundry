from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_list_entities(client: TestClient, auth_token: str) -> None:
    with patch("app.routers.graph.GraphRepository") as MockGraph:
        MockGraph.return_value.get_entities = AsyncMock(
            return_value=[
                {"id": "entity:neo4j", "name": "Neo4j", "label": "Technology"},
                {"id": "entity:qdrant", "name": "Qdrant", "label": "Technology"},
            ]
        )

        response = client.get(
            "/api/v1/graph/entities",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Neo4j"


def test_expand_entity_success(client: TestClient, auth_token: str) -> None:
    with patch("app.routers.graph.GraphRepository") as MockGraph:
        MockGraph.return_value.expand_entity = AsyncMock(
            return_value={
                "id": "entity:neo4j",
                "name": "Neo4j",
                "label": "Technology",
                "related": [
                    {"id": "entity:graph", "name": "Graph", "label": "Concept"},
                ],
            }
        )
        MockGraph.return_value.get_chunks_by_ids = AsyncMock(return_value=[])

        response = client.get(
            "/api/v1/graph/expand/entity:neo4j",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["entity"]["id"] == "entity:neo4j"
    assert len(data["related_entities"]) == 1


def test_expand_entity_not_found(client: TestClient, auth_token: str) -> None:
    with patch("app.routers.graph.GraphRepository") as MockGraph:
        MockGraph.return_value.expand_entity = AsyncMock(return_value=None)

        response = client.get(
            "/api/v1/graph/expand/entity:missing",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

    assert response.status_code == 404
