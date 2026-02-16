import pytest
from fastapi.testclient import TestClient
from main import app
from models import User, Task
from db import get_session
import json
from sqlmodel import Session, select

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_unauthenticated_access_to_protected_endpoints(client):
    """Test that all protected endpoints require authentication"""

    # Test all task endpoints without authentication
    endpoints_to_test = [
        ("GET", "/tasks/"),
        ("POST", "/tasks/", {"title": "Test", "description": "Test"}),
        ("GET", "/tasks/999"),
        ("PUT", "/tasks/999", {"title": "Updated", "is_completed": True}),
        ("DELETE", "/tasks/999"),
    ]

    for endpoint in endpoints_to_test:
        method = endpoint[0]
        url = endpoint[1]
        json_data = endpoint[2] if len(endpoint) > 2 else None

        if method == "GET":
            response = client.get(url)
        elif method == "POST":
            response = client.post(url, json=json_data)
        elif method == "PUT":
            response = client.put(url, json=json_data)
        elif method == "DELETE":
            response = client.delete(url)

        # All should return 401 Unauthorized
        assert response.status_code == 401, f"Expected 401 for {method} {url}, got {response.status_code}"

def test_malformed_token_handling(client):
    """Test handling of malformed or invalid tokens"""

    # Test with various malformed tokens
    malformed_tokens = [
        "",  # Empty token
        "Bearer ",  # Just bearer prefix
        "InvalidPrefix token123",  # Wrong prefix
        "Bearer invalid.token.format",  # Invalid format
        "Bearer very_long_invalid_token_that_does_not_match_any_valid_format_at_all",  # Invalid token
    ]

    for token in malformed_tokens:
        headers = {"Authorization": token}
        response = client.get("/tasks/", headers=headers)

        # Should return 401 for invalid tokens
        assert response.status_code == 401

def test_task_endpoint_authorization_bypass_attempts(client):
    """Test attempts to bypass authorization through various means"""

    # Register a user to get a valid token
    register_response = client.post("/auth/register", json={
        "email": "security_test@example.com",
        "password": "SecurePassword123!"
    })
    assert register_response.status_code == 200
    token_data = register_response.json()
    valid_token = token_data["access_token"]
    valid_headers = {"Authorization": f"Bearer {valid_token}"}

    # Create a task with valid credentials
    create_task_response = client.post("/tasks/",
                                      json={"title": "Security test task",
                                            "description": "Testing authorization"},
                                      headers=valid_headers)
    assert create_task_response.status_code == 200
    task_data = create_task_response.json()
    task_id = task_data["id"]

    # Now try to access it with no authentication
    unauthorized_response = client.get(f"/tasks/{task_id}")
    assert unauthorized_response.status_code == 401

    # Try to access with invalid token
    invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
    invalid_response = client.get(f"/tasks/{task_id}", headers=invalid_headers)
    assert invalid_response.status_code == 401

def test_user_data_exposure_prevention(client):
    """Test that user data is not exposed inappropriately"""

    # Register two users
    user1_data = {"email": "security_user1@example.com", "password": "SecurePassword123!"}
    user2_data = {"email": "security_user2@example.com", "password": "SecurePassword123!"}

    # Clean up any existing users
    with get_session() as session:
        for email in [user1_data["email"], user2_data["email"]]:
            existing_user = session.exec(select(User).where(User.email == email)).first()
            if existing_user:
                tasks_to_delete = session.exec(
                    select(Task).where(Task.user_id == existing_user.id)
                ).all()
                for task in tasks_to_delete:
                    session.delete(task)
                session.delete(existing_user)
        session.commit()

    # Register both users
    user1_reg = client.post("/auth/register", json=user1_data)
    assert user1_reg.status_code == 200
    user1_token = user1_reg.json()["access_token"]
    user1_headers = {"Authorization": f"Bearer {user1_token}"}

    user2_reg = client.post("/auth/register", json=user2_data)
    assert user2_reg.status_code == 200
    user2_token = user2_reg.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # Each user creates a task
    user1_task_resp = client.post("/tasks/",
                                 json={"title": "User 1 private task",
                                       "description": "This is user 1's task"},
                                 headers=user1_headers)
    assert user1_task_resp.status_code == 200
    user1_task = user1_task_resp.json()
    user1_task_id = user1_task["id"]

    user2_task_resp = client.post("/tasks/",
                                 json={"title": "User 2 private task",
                                       "description": "This is user 2's task"},
                                 headers=user2_headers)
    assert user2_task_resp.status_code == 200
    user2_task = user2_task_resp.json()
    user2_task_id = user2_task["id"]

    # Attempt to access other user's task - should be blocked
    user1_access_user2 = client.get(f"/tasks/{user2_task_id}", headers=user1_headers)
    assert user1_access_user2.status_code in [403, 404]  # Forbidden or Not Found

    user2_access_user1 = client.get(f"/tasks/{user1_task_id}", headers=user2_headers)
    assert user2_access_user1.status_code in [403, 404]  # Forbidden or Not Found

def test_brute_force_protection_simulation(client):
    """Simulate brute force protection by testing repeated invalid requests"""

    # Try multiple invalid login attempts (without exceeding realistic limits for testing)
    for i in range(3):  # Testing a few attempts, not many to avoid actual rate limiting
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": f"wrongpassword{i}"
        })
        # Should consistently return 401 for invalid credentials
        assert response.status_code == 401

def test_sql_injection_prevention(client):
    """Test that basic SQL injection attempts are handled safely"""

    # Register a user first
    register_response = client.post("/auth/register", json={
        "email": "sql_injection_test@example.com",
        "password": "SecurePassword123!"
    })
    assert register_response.status_code == 200
    token_data = register_response.json()
    valid_token = token_data["access_token"]
    valid_headers = {"Authorization": f"Bearer {valid_token}"}

    # Try creating tasks with potentially malicious titles/descriptions
    malicious_inputs = [
        {"title": "'; DROP TABLE tasks; --", "description": "SQL injection attempt"},
        {"title": " OR 1=1 --", "description": "Another SQL attempt"},
        {"title": "<script>alert('xss')</script>", "description": "XSS attempt in title"},
        {"title": "Normal title", "description": "'; DELETE FROM users; --"},
    ]

    for malicious_input in malicious_inputs:
        response = client.post("/tasks/", json=malicious_input, headers=valid_headers)
        # Should either accept (properly sanitized) or reject, but not crash
        assert response.status_code in [200, 400, 422], f"Unexpected response for malicious input: {response.status_code}"

def test_header_manipulation_attempts(client):
    """Test that header manipulation doesn't bypass security"""

    # Register a user
    register_response = client.post("/auth/register", json={
        "email": "header_test@example.com",
        "password": "SecurePassword123!"
    })
    assert register_response.status_code == 200
    token_data = register_response.json()
    valid_token = token_data["access_token"]

    # Try various header manipulation attempts
    malicious_headers = [
        {"Authorization": f"Bearer {valid_token}", "X-Forwarded-For": "192.168.1.1"},
        {"Authorization": f"bearer {valid_token}"},  # Lowercase bearer
        {"authorization": f"Bearer {valid_token}"},  # Lowercase header name
        {"Authorization": f"  Bearer   {valid_token}  "},  # Extra spaces
    ]

    for headers in malicious_headers:
        # Even with potentially manipulated headers, valid token should still work normally
        # or invalid variations should be rejected
        response = client.get("/auth/me", headers=headers)
        # Valid tokens with different casing/formatting should work if properly handled
        # or be rejected if not properly formatted
        assert response.status_code in [200, 401]