"""
Tests for health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_basic_health_check(test_client: TestClient):
    """Test basic health check endpoint."""
    response = test_client.get("/health/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "computer-use-backend"


def test_detailed_health_check(test_client: TestClient):
    """Test detailed health check endpoint."""
    response = test_client.get("/health/detailed")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy", "degraded"]
    assert data["service"] == "computer-use-backend"
    assert "components" in data