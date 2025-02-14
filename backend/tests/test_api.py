import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_analyze_query(client):
    response = client.post(
        "/api/analyze",
        json={"text": "test query", "filters": None}
    )
    assert response.status_code == 200
    assert "answer" in response.json()
