import requests
import json
from datetime import datetime, timedelta
import uuid

BASE_URL = "https://mubashirjatoi-todo-ai-chatbot.hf.space"

def test_auth_endpoints():
    print("Testing authentication endpoints...")

    # Register a test user
    email = f"test_{uuid.uuid4()}@example.com"
    password = "testpassword123"
    name = "Test User"

    print(f"Registering user: {email}")
    register_response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": email, "password": password, "name": name}
    )
    print(f"Register response: {register_response.status_code}")
    if register_response.status_code == 201:
        print("Registration successful!")
    else:
        print(f"Registration failed: {register_response.text}")
        return None, None

    # Login with the test user
    print(f"Logging in with: {email}")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password}
    )
    print(f"Login response: {login_response.status_code}")
    if login_response.status_code == 200:
        token = login_response.json()["token"]
        print("Login successful!")
        return token, email
    else:
        print(f"Login failed: {login_response.text}")
        return None, None

def test_task_endpoints(token):
    print("\nTesting task endpoints...")

    headers = {"Authorization": f"Bearer {token}"}

    # Create a task with due date
    print("Creating a task with due date...")
    due_date = (datetime.now() + timedelta(days=7)).isoformat()
    task_data = {
        "title": "Test task with due date",
        "description": "This is a test task",
        "priority": "medium",
        "category": "work",
        "due_date": due_date,
        "recurrence_pattern": "weekly"
    }

    create_response = requests.post(
        f"{BASE_URL}/api/tasks",
        json=task_data,
        headers=headers
    )
    print(f"Create task response: {create_response.status_code}")
    if create_response.status_code == 201:
        task = create_response.json()
        task_id = task["id"]
        print(f"Task created successfully with ID: {task_id}")
    else:
        print(f"Task creation failed: {create_response.text}")
        return

    # Get all tasks
    print("Getting all tasks...")
    get_tasks_response = requests.get(
        f"{BASE_URL}/api/tasks",
        headers=headers
    )
    print(f"Get tasks response: {get_tasks_response.status_code}")
    if get_tasks_response.status_code == 200:
        tasks = get_tasks_response.json()["tasks"]
        print(f"Found {len(tasks)} tasks")
    else:
        print(f"Get tasks failed: {get_tasks_response.text}")

    # Update the task
    print("Updating the task...")
    update_data = {
        "title": "Updated test task",
        "priority": "high",
        "due_date": due_date
    }

    update_response = requests.put(
        f"{BASE_URL}/api/tasks/{task_id}",
        json=update_data,
        headers=headers
    )
    print(f"Update task response: {update_response.status_code}")
    if update_response.status_code == 200:
        print("Task updated successfully")
    else:
        print(f"Task update failed: {update_response.text}")

    # Toggle task completion
    print("Toggling task completion...")
    toggle_data = {"completed": True}

    toggle_response = requests.patch(
        f"{BASE_URL}/api/tasks/{task_id}/complete",
        json=toggle_data,
        headers=headers
    )
    print(f"Toggle completion response: {toggle_response.status_code}")
    if toggle_response.status_code == 200:
        print("Task completion toggled successfully")
    else:
        print(f"Toggle completion failed: {toggle_response.text}")

    # Delete the task
    print("Deleting the task...")
    delete_response = requests.delete(
        f"{BASE_URL}/api/tasks/{task_id}",
        headers=headers
    )
    print(f"Delete task response: {delete_response.status_code}")
    if delete_response.status_code == 204:
        print("Task deleted successfully")
    else:
        print(f"Task deletion failed: {delete_response.text}")

def main():
    print("Starting API endpoint tests...")

    # Test authentication
    token, email = test_auth_endpoints()

    if token:
        # Test task operations
        test_task_endpoints(token)

        print("\nAPI tests completed!")
    else:
        print("\nAPI tests failed at authentication step.")

if __name__ == "__main__":
    main()