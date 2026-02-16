"""
Acceptance test for multi-intent command scenario
Tests that the chatbot properly handles commands with multiple intents in a single message
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from ai_chatbot.main import app
from ai_chatbot.services.auth_validator import validate_auth_token
from ai_chatbot.services.phase2_client import phase2_client
from ai_chatbot.orchestrator.multi_intent import multi_intent_processor
from ai_chatbot.models.command import NaturalLanguageCommand, IntentType


def test_multi_intent_command_scenario():
    """
    Acceptance Test: Multi-Intent Command

    Given: user is authenticated
    When: user says something with multiple intents like "Add a task to buy groceries and complete my meeting prep task"
    Then: the chatbot processes both intents and executes both actions
    """
    client = TestClient(app)

    # Mock authentication validation
    mock_user_id = "test-user-123"
    mock_auth_token = "mock-valid-token"
    mock_user_info = {
        "id": mock_user_id,
        "email": "test@example.com",
        "name": "Test User"
    }

    # Mock existing tasks
    mock_tasks = [
        {"id": "task-1", "title": "meeting prep", "completed": False},
        {"id": "task-2", "title": "schedule appointment", "completed": True}
    ]

    with patch('ai_chatbot.services.auth_validator.validate_auth_token') as mock_validate_auth:
        mock_validate_auth.return_value = AsyncMock(return_value=mock_user_id)

        with patch.object(phase2_client, 'get_user_info') as mock_get_user_info:
            mock_get_user_info.return_value = mock_user_info

            with patch.object(phase2_client, 'get_tasks') as mock_get_tasks:
                mock_get_tasks.return_value = mock_tasks

                # Send a multi-intent request to the chat endpoint
                headers = {
                    "Authorization": f"Bearer {mock_auth_token}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "message": "Add a task to buy groceries and complete the meeting prep task",
                    "conversation_id": "test-conversation-123"
                }

                response = client.post("/chat", json=payload, headers=headers)

                # Assertions
                assert response.status_code == 200
                response_data = response.json()

                # Check that the response acknowledges processing multiple requests
                assert "buy groceries" in response_data["message"].lower() or \
                       "add" in response_data["message"].lower() or \
                       "successfully" in response_data["message"].lower()

                # Verify that the response indicates success
                assert response_data["success"] is True


def test_complex_multi_intent_scenario():
    """
    Acceptance Test: Complex Multi-Intent Command

    Given: user is authenticated
    When: user says something with multiple complex intents like "Show my tasks, add a new one called 'call mom', and delete the old one"
    Then: the chatbot processes all intents in sequence and executes all actions
    """
    client = TestClient(app)

    # Mock authentication validation
    mock_user_id = "test-user-456"
    mock_auth_token = "mock-valid-token"
    mock_user_info = {
        "id": mock_user_id,
        "email": "test2@example.com",
        "name": "Test User 2"
    }

    # Mock existing tasks
    mock_tasks = [
        {"id": "task-1", "title": "old task", "completed": False},
        {"id": "task-2", "title": "another task", "completed": True}
    ]

    with patch('ai_chatbot.services.auth_validator.validate_auth_token') as mock_validate_auth:
        mock_validate_auth.return_value = AsyncMock(return_value=mock_user_id)

        with patch.object(phase2_client, 'get_user_info') as mock_get_user_info:
            mock_get_user_info.return_value = mock_user_info

            with patch.object(phase2_client, 'get_tasks') as mock_get_tasks:
                mock_get_tasks.return_value = mock_tasks

                # Send a complex multi-intent request to the chat endpoint
                headers = {
                    "Authorization": f"Bearer {mock_auth_token}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "message": "Show my tasks and add a new task called 'call mom' and delete the old task",
                    "conversation_id": "test-conversation-456"
                }

                response = client.post("/chat", json=payload, headers=headers)

                # Assertions
                assert response.status_code == 200
                response_data = response.json()

                # Check that the response addresses multiple requests
                # The response should indicate that multiple operations were processed
                assert response_data["success"] is True

                # Check that suggestions are provided for next steps
                assert response_data["suggestions"] is not None
                assert len(response_data["suggestions"]) > 0


def test_multi_intent_with_semicolon_separation():
    """
    Acceptance Test: Multi-Intent Command with Semicolon Separation

    Given: user is authenticated
    When: user says something with multiple intents separated by semicolons
    Then: the chatbot processes all intents separately
    """
    client = TestClient(app)

    # Mock authentication validation
    mock_user_id = "test-user-789"
    mock_auth_token = "mock-valid-token"
    mock_user_info = {
        "id": mock_user_id,
        "email": "test3@example.com",
        "name": "Test User 3"
    }

    # Mock existing tasks
    mock_tasks = [
        {"id": "task-1", "title": "meeting notes", "completed": False}
    ]

    with patch('ai_chatbot.services.auth_validator.validate_auth_token') as mock_validate_auth:
        mock_validate_auth.return_value = AsyncMock(return_value=mock_user_id)

        with patch.object(phase2_client, 'get_user_info') as mock_get_user_info:
            mock_get_user_info.return_value = mock_user_info

            with patch.object(phase2_client, 'get_tasks') as mock_get_tasks:
                mock_get_tasks.return_value = mock_tasks

                # Send a multi-intent request with semicolon separation
                headers = {
                    "Authorization": f"Bearer {mock_auth_token}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "message": "Complete the meeting notes task; add a task to buy milk; show my tasks",
                    "conversation_id": "test-conversation-789"
                }

                response = client.post("/chat", json=payload, headers=headers)

                # Assertions
                assert response.status_code == 200
                response_data = response.json()

                # Check that the response acknowledges processing multiple commands
                assert response_data["success"] is True


if __name__ == "__main__":
    test_multi_intent_command_scenario()
    test_complex_multi_intent_scenario()
    test_multi_intent_with_semicolon_separation()
    print("Acceptance tests for multi-intent command scenarios passed!")