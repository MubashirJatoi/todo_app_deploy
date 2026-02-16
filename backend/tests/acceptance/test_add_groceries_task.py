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


def test_add_groceries_task_scenario(client):
    """
    Acceptance test for "Add a task: Buy groceries" scenario
    """
    # Register a test user first
    test_email = "test_grocery_user@example.com"
    test_password = "SecurePassword123!"

    # Clean up any existing user first
    # Note: In a real implementation, you'd have a way to clean up test users

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
        # Configure the mock to return a successful response for the groceries task
        mock_response = ChatResponse(
            conversation_id=str(uuid.uuid4()),
            response="I've created the task: 'Buy groceries'",
            intent="CREATE_TASK",
            entities={"task_title": "Buy groceries"},
            suggestions=["Mark 'Buy groceries' as complete when done", "Show me all my tasks", "Add another task"]
        )

        mock_workflow.process_chat_message.return_value = mock_response

        # Make the request to the chat endpoint with the groceries command
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_response = client.post("/api/chat",
                                  json={"message": "Add a task: Buy groceries"},
                                  headers=headers)

        # Assert the response is successful
        assert chat_response.status_code == 200

        response_data = chat_response.json()
        assert "Buy groceries" in response_data["response"]
        assert response_data["intent"] == "CREATE_TASK"
        assert "Buy groceries" in response_data["entities"]["task_title"]


def test_add_groceries_task_scenario_alternative_phrasing(client):
    """
    Acceptance test for alternative phrasing of "Add a task: Buy groceries" scenario
    """
    # Register a test user first
    test_email = "test_grocery_alt_user@example.com"
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
            response="I've created the task: 'Buy groceries'",
            intent="CREATE_TASK",
            entities={"task_title": "Buy groceries"},
            suggestions=[]
        )

        mock_workflow.process_chat_message.return_value = mock_response

        # Test alternative phrasing
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_response = client.post("/api/chat",
                                  json={"message": "Create a task to buy groceries"},
                                  headers=headers)

        # Assert the response is successful
        assert chat_response.status_code == 200

        response_data = chat_response.json()
        assert "Buy groceries" in response_data["response"] or "buy groceries" in response_data["response"]
        assert response_data["intent"] == "CREATE_TASK"


def test_add_groceries_task_integration(client):
    """
    Integration test for "Add a task: Buy groceries" scenario that tests the full flow
    """
    # This test assumes the AI chatbot components are working properly
    # and tests the actual API endpoint without mocking

    # Register a test user first
    test_email = "test_grocery_integration@example.com"
    test_password = "SecurePassword123!"

    # Clean up any existing user first by attempting login (which will fail if doesn't exist)
    # Then register
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

    # Make the request to the chat endpoint with the groceries command
    headers = {"Authorization": f"Bearer {auth_token}"}
    chat_response = client.post("/api/chat",
                              json={"message": "Add a task: Buy groceries"},
                              headers=headers)

    # The response should be successful (though the actual content depends on the AI implementation)
    assert chat_response.status_code == 200

    response_data = chat_response.json()
    # At minimum, we expect a response with a conversation ID
    assert "conversation_id" in response_data
    assert "response" in response_data