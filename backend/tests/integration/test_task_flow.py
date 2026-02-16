import pytest
from fastapi.testclient import TestClient
from main import app
from models import User, Task
from db import get_session
import json
from sqlmodel import Session, select
from auth import create_access_token

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def authenticated_client(client):
    """Provides an authenticated client with a test user"""
    # Create a test user
    test_email = "task_integration_test@example.com"
    test_password = "SecurePassword123!"

    # Clean up any existing test user
    with get_session() as session:
        existing_user = session.exec(select(User).where(User.email == test_email)).first()
        if existing_user:
            # Delete associated tasks first due to foreign key constraint
            tasks_to_delete = session.exec(
                select(Task).where(Task.user_id == existing_user.id)
            ).all()
            for task in tasks_to_delete:
                session.delete(task)
            session.delete(existing_user)
            session.commit()

    # Register the user
    register_response = client.post("/auth/register", json={
        "email": test_email,
        "password": test_password
    })

    assert register_response.status_code == 200
    reg_data = register_response.json()

    # Create authenticated headers
    headers = {"Authorization": f"Bearer {reg_data['access_token']}"}

    yield client, headers, reg_data

def test_complete_task_management_flow(authenticated_client):
    """Integration test for the complete task management flow"""
    client, headers, user_data = authenticated_client

    # Step 1: Create a new task
    create_response = client.post("/tasks/",
                                json={"title": "Integration test task",
                                      "description": "Test task for integration flow"},
                                headers=headers)

    assert create_response.status_code == 200
    created_task = create_response.json()

    assert created_task["title"] == "Integration test task"
    assert created_task["description"] == "Test task for integration flow"
    assert created_task["is_completed"] is False
    assert "id" in created_task

    task_id = created_task["id"]

    # Step 2: Retrieve the created task
    get_single_response = client.get(f"/tasks/{task_id}", headers=headers)
    assert get_single_response.status_code == 200

    retrieved_task = get_single_response.json()
    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == "Integration test task"

    # Step 3: Retrieve all tasks and verify the task is in the list
    get_all_response = client.get("/tasks/", headers=headers)
    assert get_all_response.status_code == 200

    tasks_list = get_all_response.json()
    assert isinstance(tasks_list, list)
    assert len(tasks_list) >= 1

    # Find our task in the list
    our_task = next((task for task in tasks_list if task["id"] == task_id), None)
    assert our_task is not None
    assert our_task["title"] == "Integration test task"

    # Step 4: Update the task
    update_response = client.put(f"/tasks/{task_id}",
                               json={"title": "Updated integration test task",
                                     "description": "Updated description",
                                     "is_completed": True},
                               headers=headers)

    assert update_response.status_code == 200
    updated_task = update_response.json()

    assert updated_task["id"] == task_id
    assert updated_task["title"] == "Updated integration test task"
    assert updated_task["description"] == "Updated description"
    assert updated_task["is_completed"] is True

    # Step 5: Verify the update persisted by retrieving again
    verify_update_response = client.get(f"/tasks/{task_id}", headers=headers)
    assert verify_update_response.status_code == 200

    verified_task = verify_update_response.json()
    assert verified_task["id"] == task_id
    assert verified_task["title"] == "Updated integration test task"
    assert verified_task["is_completed"] is True

    # Step 6: Delete the task
    delete_response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 200

    # Step 7: Verify the task is gone
    get_deleted_response = client.get(f"/tasks/{task_id}", headers=headers)
    assert get_deleted_response.status_code == 404

def test_task_validation(authenticated_client):
    """Test task validation rules"""
    client, headers, user_data = authenticated_client

    # Try to create a task without a title (should fail)
    bad_request_response = client.post("/tasks/",
                                     json={"description": "Task without title"},
                                     headers=headers)

    # This might return 422 for validation error or 400, depending on implementation
    assert bad_request_response.status_code in [400, 422]

def test_user_cannot_access_other_users_tasks(client):
    """Test that a user cannot access another user's tasks"""
    # Create first user and task
    user1_email = "user1_task_test@example.com"
    user1_password = "Password123!"

    # Clean up any existing users
    with get_session() as session:
        existing_user1 = session.exec(select(User).where(User.email == user1_email)).first()
        if existing_user1:
            tasks_to_delete = session.exec(
                select(Task).where(Task.user_id == existing_user1.id)
            ).all()
            for task in tasks_to_delete:
                session.delete(task)
            session.delete(existing_user1)

        existing_user2 = session.exec(select(User).where(User.email == "user2_task_test@example.com")).first()
        if existing_user2:
            tasks_to_delete = session.exec(
                select(Task).where(Task.user_id == existing_user2.id)
            ).all()
            for task in tasks_to_delete:
                session.delete(task)
            session.delete(existing_user2)

        session.commit()

    # Register first user
    user1_reg = client.post("/auth/register", json={
        "email": user1_email,
        "password": user1_password
    })
    assert user1_reg.status_code == 200
    user1_token = user1_reg.json()["access_token"]
    user1_headers = {"Authorization": f"Bearer {user1_token}"}

    # Register second user
    user2_reg = client.post("/auth/register", json={
        "email": "user2_task_test@example.com",
        "password": "Password123!"
    })
    assert user2_reg.status_code == 200
    user2_token = user2_reg.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User 1 creates a task
    task_response = client.post("/tasks/",
                              json={"title": "User 1's private task",
                                    "description": "This should be private"},
                              headers=user1_headers)

    assert task_response.status_code == 200
    user1_task = task_response.json()
    user1_task_id = user1_task["id"]

    # User 2 tries to access User 1's task (should fail)
    access_other_response = client.get(f"/tasks/{user1_task_id}", headers=user2_headers)

    # This should either return 404 (not found) or 403 (forbidden) depending on implementation
    # Both are acceptable for security - preventing enumeration vs explicit denial
    assert access_other_response.status_code in [403, 404]