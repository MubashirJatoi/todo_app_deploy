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


def test_show_completed_tasks_scenario(client):
    """
    Acceptance test for "Show only completed tasks" scenario
    """
    # Register a test user first
    test_email = "test_filter_completed_user@example.com"
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

    # Mock the AI chatbot components to ensure they respond correctly for filtering
    with patch('ai_chatbot.orchestrator.workflow.chat_processing_workflow') as mock_workflow:
        # Configure the mock to return a successful response for the completed tasks filter
        mock_response = ChatResponse(
            conversation_id=str(uuid.uuid4()),
            response="I found 2 completed tasks: 'Meeting preparation', 'Email response'",
            intent="FILTER_TASKS",
            entities={"status": "completed"},
            suggestions=["Show all my tasks", "Show pending tasks", "Add a new task"]
        )

        mock_workflow.process_chat_message.return_value = mock_response

        # Make the request to the chat endpoint with the filter command
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_response = client.post("/api/chat",
                                  json={"message": "Show only completed tasks"},
                                  headers=headers)

        # Assert the response is successful
        assert chat_response.status_code == 200

        response_data = chat_response.json()
        assert "completed" in response_data["response"].lower()
        assert response_data["intent"] == "FILTER_TASKS"
        assert response_data["entities"]["status"] == "completed"


def test_show_completed_tasks_scenario_alternative_phrasing(client):
    """
    Acceptance test for alternative phrasing of "Show only completed tasks" scenario
    """
    # Register a test user first
    test_email = "test_filter_completed_alt_user@example.com"
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
        # Configure the mock to return a successful response for the completed tasks filter
        mock_response = ChatResponse(
            conversation_id=str(uuid.uuid4()),
            response="I found 1 completed task: 'Project review'",
            intent="FILTER_TASKS",
            entities={"status": "completed"},
            suggestions=[]
        )

        mock_workflow.process_chat_message.return_value = mock_response

        # Test alternative phrasing
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_response = client.post("/api/chat",
                                  json={"message": "Display only my completed tasks"},
                                  headers=headers)

        # Assert the response is successful
        assert chat_response.status_code == 200

        response_data = chat_response.json()
        assert "completed" in response_data["response"].lower()
        assert response_data["intent"] == "FILTER_TASKS"


def test_show_completed_tasks_integration(client):
    """
    Integration test for "Show only completed tasks" scenario that tests the full flow
    """
    # This test assumes the AI chatbot components are working properly
    # and tests the actual API endpoint without mocking

    # Register a test user first
    test_email = "test_filter_completed_integration@example.com"
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

    # Make the request to the chat endpoint with the filter command
    headers = {"Authorization": f"Bearer {auth_token}"}
    chat_response = client.post("/api/chat",
                              json={"message": "Show only completed tasks"},
                              headers=headers)

    # The response should be successful (though the actual content depends on the AI implementation)
    assert chat_response.status_code == 200

    response_data = chat_response.json()
    # At minimum, we expect a response with a conversation ID
    assert "conversation_id" in response_data
    assert "response" in response_data