from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<html" in response.text


def test_liveness_probe():
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readiness_probe():
    response = client.get("/readyz")

    assert response.status_code == 200


def test_echo_endpoint():
    response = client.post(
        "/echo",
        json={"message": "hello"}
    )

    assert response.status_code == 200