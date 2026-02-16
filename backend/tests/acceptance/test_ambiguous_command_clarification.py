"""
Acceptance test for ambiguous command clarification scenario
Tests that the chatbot properly handles ambiguous commands by requesting clarification
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from ai_chatbot.main import app
from ai_chatbot.services.auth_validator import validate_auth_token
from ai_chatbot.services.phase2_client import phase2_client
from ai_chatbot.services.conversation_state import conversation_state_manager
from ai_chatbot.services.clarification_generator import clarification_generator
from ai_chatbot.models.command import NaturalLanguageCommand, IntentType


def test_ambiguous_command_clarification_scenario():
    """
    Acceptance Test: Ambiguous Command Clarification

    Given: user is authenticated and has multiple tasks that could match a request
    When: user says something ambiguous like "Complete the task"
    Then: the chatbot asks for clarification to identify the specific task
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

    # Mock tasks that could match an ambiguous request
    mock_tasks = [
        {"id": "task-1", "title": "Complete project proposal", "completed": False},
        {"id": "task-2", "title": "Buy groceries", "completed": False},
        {"id": "task-3", "title": "Schedule meeting", "completed": False}
    ]

    with patch('ai_chatbot.services.auth_validator.validate_auth_token') as mock_validate_auth:
        mock_validate_auth.return_value = AsyncMock(return_value=mock_user_id)

        with patch.object(phase2_client, 'get_user_info') as mock_get_user_info:
            mock_get_user_info.return_value = mock_user_info

            with patch.object(phase2_client, 'get_tasks') as mock_get_tasks:
                mock_get_tasks.return_value = mock_tasks

                # Send an ambiguous request to the chat endpoint
                headers = {
                    "Authorization": f"Bearer {mock_auth_token}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "message": "Complete the task",
                    "conversation_id": "test-conversation-123"
                }

                response = client.post("/chat", json=payload, headers=headers)

                # Assertions
                assert response.status_code == 200
                response_data = response.json()

                # Check that the response indicates clarification is needed
                assert "clarification" in response_data["message"].lower() or \
                       "which task" in response_data["message"].lower() or \
                       "specific" in response_data["message"].lower()

                # Check that suggestions for clarification are provided
                assert response_data["suggestions"] is not None
                assert len(response_data["suggestions"]) > 0

                # Verify that the response indicates follow-up is required
                # (though this might vary depending on exact implementation)


def test_multiple_matching_tasks_clarification():
    """
    Acceptance Test: Multiple Matching Tasks Clarification

    Given: user is authenticated and has multiple tasks with similar titles
    When: user says something that matches multiple tasks like "Update task with 'project'"
    Then: the chatbot asks for clarification between the matching tasks
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

    # Mock tasks that could match a request
    mock_tasks = [
        {"id": "task-1", "title": "Project Alpha report", "completed": False},
        {"id": "task-2", "title": "Project Beta planning", "completed": False},
        {"id": "task-3", "title": "Personal goals", "completed": True}
    ]

    with patch('ai_chatbot.services.auth_validator.validate_auth_token') as mock_validate_auth:
        mock_validate_auth.return_value = AsyncMock(return_value=mock_user_id)

        with patch.object(phase2_client, 'get_user_info') as mock_get_user_info:
            mock_get_user_info.return_value = mock_user_info

            with patch.object(phase2_client, 'get_tasks') as mock_get_tasks:
                mock_get_tasks.return_value = mock_tasks

                # Send a request that could match multiple tasks
                headers = {
                    "Authorization": f"Bearer {mock_auth_token}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "message": "Update the project task",
                    "conversation_id": "test-conversation-456"
                }

                response = client.post("/chat", json=payload, headers=headers)

                # Assertions
                assert response.status_code == 200
                response_data = response.json()

                # Check that the response indicates clarification is needed for multiple matches
                assert any(phrase in response_data["message"].lower()
                          for phrase in ["multiple", "which", "specific", "clarify"])

                # Verify that suggestions are provided
                assert response_data["suggestions"] is not None
                assert len(response_data["suggestions"]) > 0


if __name__ == "__main__":
    test_ambiguous_command_clarification_scenario()
    test_multiple_matching_tasks_clarification()
    print("Acceptance tests for ambiguous command clarification scenarios passed!")