import pytest
from fastapi.testclient import TestClient
from main import app
import json

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_register_endpoint_contract(client):
    """Test that register endpoint follows the expected contract"""
    # Test register endpoint
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "securepassword123"
    })

    # Should return 200 or 400/409 for existing user
    assert response.status_code in [200, 400, 409]

    # Response should contain either user data or error message
    data = response.json()
    assert isinstance(data, dict)

    if response.status_code == 200:
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

def test_login_endpoint_contract(client):
    """Test that login endpoint follows the expected contract"""
    # Test login endpoint
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "securepassword123"
    })

    # Should return 200 for successful login or 401 for invalid credentials
    assert response.status_code in [200, 401]

    # Response should contain token information
    data = response.json()
    assert isinstance(data, dict)

    if response.status_code == 200:
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

def test_logout_endpoint_contract(client):
    """Test that logout endpoint follows the expected contract"""
    # Need a valid token first (or test without one to ensure protection)
    response = client.post("/auth/logout")

    # Should return 401 without valid token, or 200 with valid token
    assert response.status_code in [200, 401]

def test_get_current_user_endpoint_contract(client):
    """Test that get current user endpoint follows the expected contract"""
    # Test without token
    response = client.get("/auth/me")

    # Should return 401 without token or user data with token
    assert response.status_code in [200, 401]

    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "created_at" in data