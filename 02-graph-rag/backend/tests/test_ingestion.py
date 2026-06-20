from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.graph import build_relationships, extract_entities
from app.ingestion import _chunk_text


def test_chunk_text() -> None:
    text = " ".join(str(i) for i in range(100))
    chunks = _chunk_text(text, chunk_size=20, overlap=5)
    assert len(chunks) > 1
    # Overlap check: second chunk should end with some words from first chunk's tail
    assert len(chunks[0].split()) == 20


def test_extract_entities() -> None:
    text = "Graph RAG uses Neo4j and Qdrant. It is built with Python."
    entities = extract_entities(text, chunk_id="c1")
    names = {e["name"] for e in entities}
    assert "Graph RAG" in names or "Neo4j" in names
    for e in entities:
        assert e["id"].startswith("entity:")
        assert e["chunk_id"] == "c1"


def test_build_relationships() -> None:
    entities = [
        {"id": "entity:a", "name": "A"},
        {"id": "entity:b", "name": "B"},
        {"id": "entity:c", "name": "C"},
    ]
    rels = build_relationships(entities, chunk_id="c1")
    assert len(rels) == 3  # 3 choose 2
    for r in rels:
        assert r["type"] == "CO_OCCURS_WITH"
        assert r["chunk_id"] == "c1"


async def test_ingestion_service() -> None:
    from app.ingestion import IngestionService
    from app.models import Document

    service = IngestionService()
    service.dense.upsert = AsyncMock(return_value=2)
    service.graph.ingest_document_graph = AsyncMock(return_value=(4, 3))

    docs = [
        Document(id="doc-1", text="Graph RAG uses Neo4j and Qdrant.", metadata={"source": "test"})
    ]
    result = await service.ingest(docs)

    assert result.indexed == 2
    assert result.entities_created == 4
    assert result.relationships_created == 3
    assert len(result.errors) == 0
    service.dense.upsert.assert_called_once()


async def test_ingestion_service_partial_failure() -> None:
    from app.ingestion import IngestionService
    from app.models import Document

    service = IngestionService()
    service.dense.upsert = AsyncMock(side_effect=RuntimeError("qdrant down"))
    service.graph.ingest_document_graph = AsyncMock(return_value=(0, 0))

    docs = [Document(id="doc-1", text="Graph RAG uses Neo4j.", metadata={})]
    result = await service.ingest(docs)

    assert result.indexed == 0
    assert len(result.errors) >= 1


def test_ingest_endpoint(client: TestClient, auth_token: str) -> None:
    from app.ingestion import IngestionService

    with patch.object(
        IngestionService,
        "ingest",
        new=AsyncMock(
            return_value={
                "indexed": 2,
                "entities_created": 4,
                "relationships_created": 3,
                "errors": [],
            }
        ),
    ):
        response = client.post(
            "/api/v1/ingest",
            json={
                "documents": [
                    {"id": "doc-1", "text": "Graph RAG uses Neo4j.", "metadata": {"source": "test"}},
                    {"id": "doc-2", "text": "Qdrant stores vectors.", "metadata": {"source": "test"}},
                ]
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["indexed"] == 2
    assert data["entities_created"] == 4
    assert data["relationships_created"] == 3
