"""
Acceptance test for "What is my email?" scenario
Tests that authenticated users can ask the chatbot for their email address
"""
import pytest
import os
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from ai_chatbot.api.chat_endpoint import router
from ai_chatbot.main import app
from ai_chatbot.services.auth_validator import validate_auth_token
from ai_chatbot.services.phase2_client import phase2_client


def test_what_is_my_email_scenario():
    """
    Acceptance Test: What is my email?

    Given: user is authenticated
    When: user says "What is my email?"
    Then: the chatbot returns the user's email address
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

    with patch('ai_chatbot.services.auth_validator.validate_auth_token') as mock_validate_auth:
        mock_validate_auth.return_value = AsyncMock(return_value=mock_user_id)

        with patch.object(phase2_client, 'get_user_info') as mock_get_user_info:
            mock_get_user_info.return_value = mock_user_info

            # Send the request to the chat endpoint
            headers = {
                "Authorization": f"Bearer {mock_auth_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "message": "What is my email?",
                "conversation_id": "test-conversation-123"
            }

            response = client.post("/chat", json=payload, headers=headers)

            # Assertions
            assert response.status_code == 200
            response_data = response.json()

            # Check that the response contains the user's email
            assert "test@example.com" in response_data["message"]
            assert response_data["success"] is True
            assert "email" in response_data["message"].lower()


def test_who_am_i_scenario():
    """
    Acceptance Test: Who am I?

    Given: user is authenticated
    When: user says "Who am I?"
    Then: the chatbot confirms the user's identity
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

    with patch('ai_chatbot.services.auth_validator.validate_auth_token') as mock_validate_auth:
        mock_validate_auth.return_value = AsyncMock(return_value=mock_user_id)

        with patch.object(phase2_client, 'get_user_info') as mock_get_user_info:
            mock_get_user_info.return_value = mock_user_info

            # Send the request to the chat endpoint
            headers = {
                "Authorization": f"Bearer {mock_auth_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "message": "Who am I?",
                "conversation_id": "test-conversation-123"
            }

            response = client.post("/chat", json=payload, headers=headers)

            # Assertions
            assert response.status_code == 200
            response_data = response.json()

            # Check that the response confirms the user's identity
            assert "test@example.com" in response_data["message"] or "Test User" in response_data["message"]
            assert response_data["success"] is True


if __name__ == "__main__":
    test_what_is_my_email_scenario()
    test_who_am_i_scenario()
    print("Acceptance tests for user identity scenarios passed!")