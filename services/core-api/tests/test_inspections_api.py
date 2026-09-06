import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["service"] == "core-api"


def test_rules_active_endpoint():
    # Attempting to fetch active rule (or 404 if not seeded)
    response = client.get("/api/v1/rules/active")
    assert response.status_code in [200, 404]
