"""
Acceptance test for destructive action confirmation scenario
Tests that the chatbot properly handles destructive actions by requesting confirmation
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from ai_chatbot.main import app
from ai_chatbot.services.auth_validator import validate_auth_token
from ai_chatbot.services.phase2_client import phase2_client
from ai_chatbot.services.confirmation_service import confirmation_service
from ai_chatbot.models.command import NaturalLanguageCommand, IntentType


def test_destructive_action_confirmation_scenario():
    """
    Acceptance Test: Destructive Action Confirmation

    Given: user is authenticated
    When: user says something destructive like "Delete all my tasks"
    Then: the chatbot requests confirmation before executing the action
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

    # Mock tasks that would be affected
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

                # Send a destructive request to the chat endpoint
                headers = {
                    "Authorization": f"Bearer {mock_auth_token}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "message": "Delete all my tasks",
                    "conversation_id": "test-conversation-123"
                }

                response = client.post("/chat", json=payload, headers=headers)

                # Assertions
                assert response.status_code == 200
                response_data = response.json()

                # Check that the response indicates confirmation is needed for destructive action
                assert "confirm" in response_data["message"].lower() or \
                       "sure" in response_data["message"].lower() or \
                       "warning" in response_data["message"].lower()

                # Check that suggestions for confirmation are provided
                assert response_data["suggestions"] is not None
                assert len(response_data["suggestions"]) > 0
                assert any("confirm" in suggestion.lower() for suggestion in response_data["suggestions"])


def test_confirmation_execution_scenario():
    """
    Acceptance Test: Confirmation Execution

    Given: user has requested a destructive action and received a confirmation request
    When: user confirms the action with the confirmation ID
    Then: the chatbot executes the destructive action
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

    # Mock tasks for deletion
    mock_tasks = [
        {"id": "task-1", "title": "Old task", "completed": False},
        {"id": "task-2", "title": "Another old task", "completed": True}
    ]

    with patch('ai_chatbot.services.auth_validator.validate_auth_token') as mock_validate_auth:
        mock_validate_auth.return_value = AsyncMock(return_value=mock_user_id)

        with patch.object(phase2_client, 'get_user_info') as mock_get_user_info:
            mock_get_user_info.return_value = mock_user_info

            with patch.object(phase2_client, 'get_tasks') as mock_get_tasks:
                mock_get_tasks.return_value = mock_tasks

                # First, trigger a destructive action to get a confirmation request
                headers = {
                    "Authorization": f"Bearer {mock_auth_token}",
                    "Content-Type": "application/json"
                }

                # Simulate the confirmation service creating a confirmation request
                # We'll test the confirmation endpoint directly
                confirmation_payload = {
                    "confirmation_id": "test-confirmation-id",
                    "action": "confirm"
                }

                # Since we're testing the confirmation mechanism, we'll mock the confirmation service
                # to simulate a real confirmation scenario
                with patch.object(confirmation_service, 'get_confirmation_status') as mock_get_status:
                    mock_confirmation = type('MockConfirmation', (), {})()
                    mock_confirmation.confirmation_id = "test-confirmation-id"
                    mock_confirmation.message = "Are you sure you want to delete all tasks?"
                    mock_confirmation.is_confirmed = True
                    mock_confirmation.is_rejected = False
                    mock_get_status.return_value = mock_confirmation

                    with patch.object(confirmation_service, 'confirm_action') as mock_confirm_action:
                        mock_confirm_action.return_value = True

                        with patch.object(confirmation_service, 'process_confirmed_action') as mock_process_action:
                            mock_process_action.return_value = type('MockResult', (), {
                                'success': True,
                                'message': 'All tasks have been deleted successfully',
                                'intent': IntentType.DELETE_TASK,
                                'suggestions': ['Add a new task', 'View remaining tasks']
                            })()

                            confirm_response = client.post("/confirm", json=confirmation_payload, headers=headers)

                            # Assertions
                            assert confirm_response.status_code == 200
                            confirm_response_data = confirm_response.json()

                            # Check that the confirmation was processed successfully
                            assert confirm_response_data["success"] is True
                            assert "deleted" in confirm_response_data["message"].lower()


def test_confirmation_rejection_scenario():
    """
    Acceptance Test: Confirmation Rejection

    Given: user has requested a destructive action and received a confirmation request
    When: user rejects the action
    Then: the chatbot cancels the destructive action
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

    with patch('ai_chatbot.services.auth_validator.validate_auth_token') as mock_validate_auth:
        mock_validate_auth.return_value = AsyncMock(return_value=mock_user_id)

        with patch.object(phase2_client, 'get_user_info') as mock_get_user_info:
            mock_get_user_info.return_value = mock_user_info

            headers = {
                "Authorization": f"Bearer {mock_auth_token}",
                "Content-Type": "application/json"
            }

            # Test rejection of a confirmation
            confirmation_payload = {
                "confirmation_id": "test-reject-confirmation-id",
                "action": "reject"
            }

            # Mock the confirmation service for rejection
            with patch.object(confirmation_service, 'reject_action') as mock_reject_action:
                mock_reject_action.return_value = True

                confirm_response = client.post("/confirm", json=confirmation_payload, headers=headers)

                # Assertions
                assert confirm_response.status_code == 200
                confirm_response_data = confirm_response.json()

                # Check that the action was rejected and cancelled
                assert confirm_response_data["success"] is True
                assert "cancelled" in confirm_response_data["message"].lower() or \
                       "rejected" in confirm_response_data["message"].lower()


if __name__ == "__main__":
    test_destructive_action_confirmation_scenario()
    test_confirmation_execution_scenario()
    test_confirmation_rejection_scenario()
    print("Acceptance tests for destructive action confirmation scenarios passed!")