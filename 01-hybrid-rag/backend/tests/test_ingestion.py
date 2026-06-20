from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_ingest_documents_success(client: TestClient, auth_token: str) -> None:
    with patch("app.ingestion.DenseRetriever") as MockDense, \
         patch("app.ingestion.SparseRetriever") as MockSparse:
        MockDense.return_value.upsert = AsyncMock(return_value=2)
        MockSparse.return_value.upsert = AsyncMock(return_value=2)

        response = client.post(
            "/api/v1/ingest",
            json={
                "documents": [
                    {"id": "doc-1", "text": "Retrieval augmented generation combines retrieval with generation.", "metadata": {"source": "wiki"}},
                ]
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["indexed"] == 4


def test_ingest_documents_validation_error(client: TestClient, auth_token: str) -> None:
    with patch("app.ingestion.DenseRetriever") as MockDense, \
         patch("app.ingestion.SparseRetriever") as MockSparse:
        MockDense.return_value.upsert = AsyncMock(return_value=0)
        MockSparse.return_value.upsert = AsyncMock(return_value=0)

        response = client.post(
            "/api/v1/ingest",
            json={"documents": []},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
    assert response.status_code == 422
