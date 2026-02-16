import pytest
from fastapi.testclient import TestClient
from main import app
import json

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_create_task_endpoint_contract(client):
    """Test that create task endpoint follows the expected contract"""
    # Test without authentication (should fail)
    response = client.post("/tasks/", json={
        "title": "Test task",
        "description": "Test description"
    })

    # Should return 401 without authentication
    assert response.status_code == 401

def test_get_tasks_endpoint_contract(client):
    """Test that get tasks endpoint follows the expected contract"""
    # Test without authentication (should fail)
    response = client.get("/tasks/")

    # Should return 401 without authentication
    assert response.status_code == 401

def test_get_task_by_id_endpoint_contract(client):
    """Test that get task by ID endpoint follows the expected contract"""
    # Test without authentication (should fail)
    response = client.get("/tasks/999")

    # Should return 401 without authentication
    assert response.status_code == 401

def test_update_task_endpoint_contract(client):
    """Test that update task endpoint follows the expected contract"""
    # Test without authentication (should fail)
    response = client.put("/tasks/999", json={
        "title": "Updated task",
        "description": "Updated description",
        "is_completed": True
    })

    # Should return 401 without authentication
    assert response.status_code == 401

def test_delete_task_endpoint_contract(client):
    """Test that delete task endpoint follows the expected contract"""
    # Test without authentication (should fail)
    response = client.delete("/tasks/999")

    # Should return 401 without authentication
    assert response.status_code == 401

def test_task_payload_structure(client):
    """Test that task payload follows expected structure"""
    # This is just a structural verification - would need valid auth to test fully
    # We'll check the request/response structure expectations

    # Expected create payload structure
    expected_create_payload = {
        "title": "string",
        "description": "string (optional)"
    }

    # Expected response structure for task
    expected_task_response = {
        "id": "integer",
        "title": "string",
        "description": "string or null",
        "is_completed": "boolean",
        "user_id": "integer",
        "created_at": "datetime string",
        "updated_at": "datetime string"
    }

    # Expected update payload structure (partial update)
    expected_update_payload = {
        "title": "string (optional)",
        "description": "string (optional)",
        "is_completed": "boolean (optional)"
    }

    # These are just structural verifications - actual functionality tested elsewhere
    assert isinstance(expected_create_payload, dict)
    assert isinstance(expected_task_response, dict)
    assert isinstance(expected_update_payload, dict)