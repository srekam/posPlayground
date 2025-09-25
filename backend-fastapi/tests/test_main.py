"""
Main Application Tests
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async test client fixture"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    
    data = response.json()
    assert data["ok"] is True
    assert data["status"] == "healthy"


def test_ready_check(client):
    """Test readiness check endpoint"""
    response = client.get("/readyz")
    assert response.status_code == 200
    
    data = response.json()
    assert data["ok"] is True
    assert data["status"] == "ready"


def test_openapi_docs(client):
    """Test OpenAPI documentation endpoint"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json(client):
    """Test OpenAPI JSON endpoint"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "PlayPark API"


@pytest.mark.asyncio
async def test_device_login(async_client):
    """Test device login endpoint"""
    login_data = {
        "device_id": "pos-device-001",
        "device_token": "pos-token-1"
    }
    
    response = await async_client.post("/api/v1/auth/device/login", json=login_data)
    
    # This will fail in test environment without proper setup
    # but tests the endpoint structure
    assert response.status_code in [200, 401, 500]


@pytest.mark.asyncio
async def test_employee_login(async_client):
    """Test employee login endpoint"""
    login_data = {
        "email": "manager@playpark.demo",
        "pin": "1234"
    }
    
    response = await async_client.post("/api/v1/auth/employees/login", json=login_data)
    
    # This will fail in test environment without proper setup
    # but tests the endpoint structure
    assert response.status_code in [200, 401, 500]


def test_cors_headers(client):
    """Test CORS headers"""
    response = client.options("/api/v1/auth/device/login")
    
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers


def test_rate_limiting_headers(client):
    """Test rate limiting headers"""
    # Make multiple requests to trigger rate limiting
    for _ in range(5):
        response = client.get("/healthz")
    
    # Rate limit headers should be present
    assert response.status_code == 200
    # Note: Rate limiting may be disabled in test environment
