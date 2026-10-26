from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "hostname" in data
    assert "python_version" in data


def test_liveness_probe():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_probe():
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_echo_endpoint():
    payload = {"message": "Test DevOps Deployment", "metadata": {"tier": "staging"}}
    response = client.post("/echo", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["received_message"] == "Test DevOps Deployment"
    assert data["metadata"]["tier"] == "staging"
    assert "processed_at" in data
    assert "processed_by" in data