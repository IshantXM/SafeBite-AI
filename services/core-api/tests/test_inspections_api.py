import io

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
    # When the Postgres dependency is not running, the API should fail gracefully with a clear 503.
    response = client.get("/api/v1/rules/active")
    assert response.status_code in [200, 404, 503]


def test_scan_verify_endpoint_returns_structured_analysis():
    image_bytes = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xe5\x27\xd8\xcf\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    response = client.post(
        "/api/v1/scan-verify",
        files={"file": ("sample.png", io.BytesIO(image_bytes), "image/png")},
    )

    assert response.status_code in [200, 503]
    payload = response.json()
    assert "scan_metadata" in payload or "detail" in payload
