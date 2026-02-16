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

def setup_test_users_and_tasks(client):
    """Helper to set up test users and their tasks"""
    # Clean up any existing test users and their tasks
    with get_session() as session:
        users_to_clean = session.exec(
            select(User).where(
                User.email.in_(["isolation_user1@example.com", "isolation_user2@example.com"])
            )
        ).all()

        for user in users_to_clean:
            # Delete associated tasks first due to foreign key constraint
            tasks_to_delete = session.exec(
                select(Task).where(Task.user_id == user.id)
            ).all()
            for task in tasks_to_delete:
                session.delete(task)
            session.delete(user)
        session.commit()

    # Create first user and authenticate
    user1_reg = client.post("/auth/register", json={
        "email": "isolation_user1@example.com",
        "password": "SecurePassword123!"
    })
    assert user1_reg.status_code == 200
    user1_token = user1_reg.json()["access_token"]
    user1_headers = {"Authorization": f"Bearer {user1_token}"}

    # Create second user and authenticate
    user2_reg = client.post("/auth/register", json={
        "email": "isolation_user2@example.com",
        "password": "SecurePassword123!"
    })
    assert user2_reg.status_code == 200
    user2_token = user2_reg.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    return user1_headers, user2_headers

def test_user_task_isolation_basic(client):
    """Basic test for user task isolation"""
    user1_headers, user2_headers = setup_test_users_and_tasks(client)

    # User 1 creates a task
    user1_task_response = client.post("/tasks/",
                                     json={"title": "User 1's task",
                                           "description": "Only for user 1"},
                                     headers=user1_headers)
    assert user1_task_response.status_code == 200
    user1_task = user1_task_response.json()
    user1_task_id = user1_task["id"]

    # User 2 creates a task
    user2_task_response = client.post("/tasks/",
                                     json={"title": "User 2's task",
                                           "description": "Only for user 2"},
                                     headers=user2_headers)
    assert user2_task_response.status_code == 200
    user2_task = user2_task_response.json()
    user2_task_id = user2_task["id"]

    # User 1 should only see their own task
    user1_tasks_response = client.get("/tasks/", headers=user1_headers)
    assert user1_tasks_response.status_code == 200
    user1_tasks = user1_tasks_response.json()

    user1_task_ids = [task["id"] for task in user1_tasks]
    assert user1_task_id in user1_task_ids
    assert user2_task_id not in user1_task_ids  # Critical: User 1 should not see User 2's task

    # User 2 should only see their own task
    user2_tasks_response = client.get("/tasks/", headers=user2_headers)
    assert user2_tasks_response.status_code == 200
    user2_tasks = user2_tasks_response.json()

    user2_task_ids = [task["id"] for task in user2_tasks]
    assert user2_task_id in user2_task_ids
    assert user1_task_id not in user2_task_ids  # Critical: User 2 should not see User 1's task

def test_cross_user_task_access_prevention(client):
    """Test that users cannot access each other's tasks by ID"""
    user1_headers, user2_headers = setup_test_users_and_tasks(client)

    # User 1 creates a task
    user1_task_response = client.post("/tasks/",
                                     json={"title": "Private task for user 1",
                                           "description": "Should not be accessible to user 2"},
                                     headers=user1_headers)
    assert user1_task_response.status_code == 200
    user1_task = user1_task_response.json()
    user1_task_id = user1_task["id"]

    # User 2 tries to access User 1's task by ID (should fail)
    access_other_task_response = client.get(f"/tasks/{user1_task_id}", headers=user2_headers)

    # Should return 404 (not found) or 403 (forbidden) - both prevent data leakage
    assert access_other_task_response.status_code in [403, 404]

    # User 2 should not be able to update User 1's task
    update_other_task_response = client.put(f"/tasks/{user1_task_id}",
                                          json={"title": "Hacked task", "is_completed": True},
                                          headers=user2_headers)
    assert update_other_task_response.status_code in [403, 404]

    # User 2 should not be able to delete User 1's task
    delete_other_task_response = client.delete(f"/tasks/{user1_task_id}", headers=user2_headers)
    assert delete_other_task_response.status_code in [403, 404]

def test_user_task_count_isolation(client):
    """Test that users see the correct count of their own tasks"""
    user1_headers, user2_headers = setup_test_users_and_tasks(client)

    # User 1 creates 3 tasks
    for i in range(3):
        response = client.post("/tasks/",
                              json={"title": f"User 1 task {i+1}",
                                    "description": f"Description for user 1 task {i+1}"},
                              headers=user1_headers)
        assert response.status_code == 200

    # User 2 creates 2 tasks
    for i in range(2):
        response = client.post("/tasks/",
                              json={"title": f"User 2 task {i+1}",
                                    "description": f"Description for user 2 task {i+1}"},
                              headers=user2_headers)
        assert response.status_code == 200

    # Verify User 1 sees exactly 3 tasks
    user1_tasks_response = client.get("/tasks/", headers=user1_headers)
    assert user1_tasks_response.status_code == 200
    user1_tasks = user1_tasks_response.json()
    assert len(user1_tasks) == 3

    # Verify User 2 sees exactly 2 tasks
    user2_tasks_response = client.get("/tasks/", headers=user2_headers)
    assert user2_tasks_response.status_code == 200
    user2_tasks = user2_tasks_response.json()
    assert len(user2_tasks) == 2

def test_database_level_isolation(client):
    """Test that data isolation is maintained at the database level"""
    user1_headers, user2_headers = setup_test_users_and_tasks(client)

    # User 1 creates several tasks
    user1_task_ids = []
    for i in range(5):
        response = client.post("/tasks/",
                              json={"title": f"User 1 task {i+1}",
                                    "description": f"Database isolation test task {i+1}"},
                              headers=user1_headers)
        assert response.status_code == 200
        task_data = response.json()
        user1_task_ids.append(task_data["id"])

    # User 2 creates several tasks
    user2_task_ids = []
    for i in range(3):
        response = client.post("/tasks/",
                              json={"title": f"User 2 task {i+1}",
                                    "description": f"Database isolation test task {i+1}"},
                              headers=user2_headers)
        assert response.status_code == 200
        task_data = response.json()
        user2_task_ids.append(task_data["id"])

    # Verify complete isolation - each user only sees their own tasks
    user1_tasks_response = client.get("/tasks/", headers=user1_headers)
    assert user1_tasks_response.status_code == 200
    user1_tasks = user1_tasks_response.json()
    user1_returned_ids = [task["id"] for task in user1_tasks]

    for task_id in user1_task_ids:
        assert task_id in user1_returned_ids

    for task_id in user2_task_ids:
        assert task_id not in user1_returned_ids  # Critical isolation check

    user2_tasks_response = client.get("/tasks/", headers=user2_headers)
    assert user2_tasks_response.status_code == 200
    user2_tasks = user2_tasks_response.json()
    user2_returned_ids = [task["id"] for task in user2_tasks]

    for task_id in user2_task_ids:
        assert task_id in user2_returned_ids

    for task_id in user1_task_ids:
        assert task_id not in user2_returned_ids  # Critical isolation check

def test_user_profile_isolation(client):
    """Test that users can only access their own profile information"""
    user1_headers, user2_headers = setup_test_users_and_tasks(client)

    # User 1 accesses their own profile
    user1_profile_response = client.get("/auth/me", headers=user1_headers)
    assert user1_profile_response.status_code == 200
    user1_profile = user1_profile_response.json()
    assert user1_profile["email"] == "isolation_user1@example.com"

    # User 2 accesses their own profile
    user2_profile_response = client.get("/auth/me", headers=user2_headers)
    assert user2_profile_response.status_code == 200
    user2_profile = user2_profile_response.json()
    assert user2_profile["email"] == "isolation_user2@example.com"

    # Verify they got different user IDs
    assert user1_profile["id"] != user2_profile["id"]