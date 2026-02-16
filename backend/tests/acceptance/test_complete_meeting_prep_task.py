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


def test_complete_meeting_prep_task_scenario(client):
    """
    Acceptance test for "Complete my meeting prep task" scenario
    """
    # Register a test user first
    test_email = "test_meeting_user@example.com"
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
        # Configure the mock to return a successful response for completing the meeting prep task
        mock_response = ChatResponse(
            conversation_id=str(uuid.uuid4()),
            response="I've marked the task 'Meeting prep' as complete!",
            intent="COMPLETE_TASK",
            entities={"task_title": "Meeting prep"},
            suggestions=["Show me my incomplete tasks", "Show me all my tasks", "Mark another task as complete"]
        )

        mock_workflow.process_chat_message.return_value = mock_response

        # Make the request to the chat endpoint with the meeting prep completion command
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_response = client.post("/api/chat",
                                  json={"message": "Complete my meeting prep task"},
                                  headers=headers)

        # Assert the response is successful
        assert chat_response.status_code == 200

        response_data = chat_response.json()
        assert "meeting prep" in response_data["response"].lower()
        assert response_data["intent"] == "COMPLETE_TASK"
        assert "Meeting prep" in str(response_data["entities"])


def test_complete_meeting_prep_task_scenario_alternative_phrasing(client):
    """
    Acceptance test for alternative phrasing of "Complete my meeting prep task" scenario
    """
    # Register a test user first
    test_email = "test_meeting_alt_user@example.com"
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
            response="I've marked the task 'Prepare for meeting' as complete!",
            intent="COMPLETE_TASK",
            entities={"task_title": "Prepare for meeting"},
            suggestions=[]
        )

        mock_workflow.process_chat_message.return_value = mock_response

        # Test alternative phrasing
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_response = client.post("/api/chat",
                                  json={"message": "Finish the meeting preparation task"},
                                  headers=headers)

        # Assert the response is successful
        assert chat_response.status_code == 200

        response_data = chat_response.json()
        assert "meeting" in response_data["response"].lower()
        assert response_data["intent"] == "COMPLETE_TASK"


def test_complete_meeting_prep_task_integration(client):
    """
    Integration test for "Complete my meeting prep task" scenario that tests the full flow
    """
    # Register a test user first
    test_email = "test_meeting_integration@example.com"
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

    # Make the request to the chat endpoint with the meeting prep completion command
    headers = {"Authorization": f"Bearer {auth_token}"}
    chat_response = client.post("/api/chat",
                              json={"message": "Complete my meeting prep task"},
                              headers=headers)

    # The response should be successful (though the actual content depends on the AI implementation)
    assert chat_response.status_code == 200

    response_data = chat_response.json()
    # At minimum, we expect a response with a conversation ID
    assert "conversation_id" in response_data
    assert "response" in response_data


def test_complete_nonexistent_meeting_prep_task(client):
    """
    Test for attempting to complete a meeting prep task that doesn't exist
    """
    # Register a test user first
    test_email = "test_nonexistent_user@example.com"
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
            response="I couldn't find any tasks containing 'meeting prep'.",
            intent="COMPLETE_TASK",
            entities={"search_term": "meeting prep"},
            suggestions=["Show me all my tasks", "Add a new task"]
        )

        mock_workflow.process_chat_message.return_value = mock_response

        # Make the request to the chat endpoint
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_response = client.post("/api/chat",
                                  json={"message": "Complete my meeting prep task"},
                                  headers=headers)

        # Assert the response is successful but indicates the task wasn't found
        assert chat_response.status_code == 200

        response_data = chat_response.json()
        assert "couldn't find" in response_data["response"].lower() or "no tasks" in response_data["response"].lower()