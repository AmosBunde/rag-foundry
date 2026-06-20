from fastapi.testclient import TestClient


def test_get_patient_success(client: TestClient, auth_token: str) -> None:
    response = client.get(
        "/api/v1/patients/pat-001",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == "pat-001"
    assert "name" in data


def test_get_patient_not_found(client: TestClient, auth_token: str) -> None:
    response = client.get(
        "/api/v1/patients/nonexistent",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404
