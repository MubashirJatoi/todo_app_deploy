import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from ai_chatbot.models.command import NaturalLanguageCommand, IntentType
from ai_chatbot.models.responses import ChatResponse
import uuid


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_delete_grocery_task_scenario(client):
    """
    Acceptance test for "Delete the grocery task" scenario
    """
    # Register a test user first
    test_email = "test_delete_user@example.com"
    test_password = "SecurePassword123!"

    # Register the user
    register_response = client.post("/api/auth/register", json={
        "email": test_email,
        "password": test_password
    })

    assert register_response.status_code in [200, 409]  # 200 if new user, 409 if already exists

    # Login to get token
    login_response = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_password
    })

    assert login_response.status_code == 200
    token_data = login_response.json()
    auth_token = token_data["access_token"]

    # Mock the AI chatbot components to ensure they respond correctly
    with patch('ai_chatbot.orchestrator.workflow.chat_processing_workflow') as mock_workflow:
        # Configure the mock to return a successful response for deleting the grocery task
        mock_response = ChatResponse(
            conversation_id=str(uuid.uuid4()),
            response="I've deleted the task: 'Buy groceries'",
            intent="DELETE_TASK",
            entities={"task_title": "Buy groceries"},
            suggestions=["Show me all my tasks", "Add a new task"]
        )

        mock_workflow.process_chat_message.return_value = mock_response

        # Make the request to the chat endpoint with the grocery task deletion command
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_response = client.post("/api/chat",
                                  json={"message": "Delete the grocery task"},
                                  headers=headers)

        # Assert the response is successful
        assert chat_response.status_code == 200

        response_data = chat_response.json()
        assert "grocery" in response_data["response"].lower() or "groceries" in response_data["response"].lower()
        assert response_data["intent"] == "DELETE_TASK"
        assert "grocery" in str(response_data["entities"]).lower()


def test_delete_grocery_task_scenario_alternative_phrasing(client):
    """
    Acceptance test for alternative phrasing of "Delete the grocery task" scenario
    """
    # Register a test user first
    test_email = "test_delete_alt_user@example.com"
    test_password = "SecurePassword123!"

    # Login to get token
    login_response = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_password
    })

    # If login fails, try registering first
    if login_response.status_code != 200:
        register_response = client.post("/api/auth/register", json={
            "email": test_email,
            "password": test_password
        })
        assert register_response.status_code in [200, 409]

        login_response = client.post("/api/auth/login", json={
            "email": test_email,
            "password": test_password
        })

    assert login_response.status_code == 200
    token_data = login_response.json()
    auth_token = token_data["access_token"]

    # Mock the AI chatbot components
    with patch('ai_chatbot.orchestrator.workflow.chat_processing_workflow') as mock_workflow:
        # Configure the mock to return a successful response
        mock_response = ChatResponse(
            conversation_id=str(uuid.uuid4()),
            response="I've deleted the task: 'Grocery shopping'",
            intent="DELETE_TASK",
            entities={"task_title": "Grocery shopping"},
            suggestions=[]
        )

        mock_workflow.process_chat_message.return_value = mock_response

        # Test alternative phrasing
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_response = client.post("/api/chat",
                                  json={"message": "Remove the grocery shopping task"},
                                  headers=headers)

        # Assert the response is successful
        assert chat_response.status_code == 200

        response_data = chat_response.json()
        assert "grocery" in response_data["response"].lower() or "shopping" in response_data["response"].lower()
        assert response_data["intent"] == "DELETE_TASK"


def test_delete_grocery_task_integration(client):
    """
    Integration test for "Delete the grocery task" scenario that tests the full flow
    """
    # Register a test user first
    test_email = "test_delete_integration@example.com"
    test_password = "SecurePassword123!"

    # Register
    register_response = client.post("/api/auth/register", json={
        "email": test_email,
        "password": test_password
    })

    assert register_response.status_code in [200, 409]  # 200 if new user, 409 if already exists

    # Login to get token
    login_response = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_password
    })

    assert login_response.status_code == 200
    token_data = login_response.json()
    auth_token = token_data["access_token"]

    # Make the request to the chat endpoint with the grocery task deletion command
    headers = {"Authorization": f"Bearer {auth_token}"}
    chat_response = client.post("/api/chat",
                              json={"message": "Delete the grocery task"},
                              headers=headers)

    # The response should be successful (though the actual content depends on the AI implementation)
    assert chat_response.status_code == 200

    response_data = chat_response.json()
    # At minimum, we expect a response with a conversation ID
    assert "conversation_id" in response_data
    assert "response" in response_data


def test_delete_nonexistent_grocery_task(client):
    """
    Test for attempting to delete a grocery task that doesn't exist
    """
    # Register a test user first
    test_email = "test_delete_nonexistent_user@example.com"
    test_password = "SecurePassword123!"

    # Register
    register_response = client.post("/api/auth/register", json={
        "email": test_email,
        "password": test_password
    })

    assert register_response.status_code in [200, 409]  # 200 if new user, 409 if already exists

    # Login to get token
    login_response = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_password
    })

    assert login_response.status_code == 200
    token_data = login_response.json()
    auth_token = token_data["access_token"]

    # Mock the AI chatbot components to simulate not finding the task
    with patch('ai_chatbot.orchestrator.workflow.chat_processing_workflow') as mock_workflow:
        # Configure the mock to return a response indicating the task wasn't found
        mock_response = ChatResponse(
            conversation_id=str(uuid.uuid4()),
            response="I couldn't find any tasks containing 'grocery'.",
            intent="DELETE_TASK",
            entities={"search_term": "grocery"},
            suggestions=["Show me all my tasks", "Add a new task"]
        )

        mock_workflow.process_chat_message.return_value = mock_response

        # Make the request to the chat endpoint
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_response = client.post("/api/chat",
                                  json={"message": "Delete the grocery task"},
                                  headers=headers)

        # Assert the response is successful but indicates the task wasn't found
        assert chat_response.status_code == 200

        response_data = chat_response.json()
        assert "couldn't find" in response_data["response"].lower() or "no tasks" in response_data["response"].lower()


def test_delete_grocery_task_with_confirmation(client):
    """
    Test for deleting a grocery task when the system requires confirmation
    """
    # Register a test user first
    test_email = "test_delete_confirm_user@example.com"
    test_password = "SecurePassword123!"

    # Register
    register_response = client.post("/api/auth/register", json={
        "email": test_email,
        "password": test_password
    })

    assert register_response.status_code in [200, 409]  # 200 if new user, 409 if already exists

    # Login to get token
    login_response = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_password
    })

    assert login_response.status_code == 200
    token_data = login_response.json()
    auth_token = token_data["access_token"]

    # Mock the AI chatbot components to simulate a confirmation requirement
    with patch('ai_chatbot.orchestrator.workflow.chat_processing_workflow') as mock_workflow:
        # First call: returns a confirmation request
        confirmation_response = ChatResponse(
            conversation_id=str(uuid.uuid4()),
            response="Are you sure you want to delete the task 'Buy groceries'? Please confirm.",
            intent="CONFIRMATION_REQUIRED",
            entities={},
            suggestions=["yes", "no"]
        )

        # Second call: simulates user saying "yes"
        deletion_response = ChatResponse(
            conversation_id=confirmation_response.conversation_id,
            response="I've deleted the task: 'Buy groceries'",
            intent="DELETE_TASK",
            entities={"task_id": "some-task-id", "task_title": "Buy groceries"},
            suggestions=["Show me all my tasks", "Add a new task"]
        )

        # Configure the mock to return confirmation first, then deletion
        mock_workflow.handle_confirmation_response.return_value = deletion_response
        mock_workflow.process_chat_message.return_value = confirmation_response

        # Make the initial request to delete the grocery task
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_response = client.post("/api/chat",
                                  json={"message": "Delete the grocery task"},
                                  headers=headers)

        # Should return confirmation request
        assert chat_response.status_code == 200

        response_data = chat_response.json()
        assert "confirm" in response_data["response"].lower()

        # Now simulate the user confirming
        confirm_response = client.post("/api/chat/confirm",
                                    json={
                                        "message": "yes",
                                        "conversation_id": response_data["conversation_id"]
                                    },
                                    headers=headers)

        # Should return the deletion confirmation
        assert confirm_response.status_code == 200

        confirm_data = confirm_response.json()
        assert "deleted" in confirm_data["response"].lower()