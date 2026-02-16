from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from pydantic import BaseModel
from ai_chatbot.orchestrator.workflow import chat_processing_workflow
from ai_chatbot.services.auth_validator import auth_validator
from ai_chatbot.utils.logging import logger
from ai_chatbot.models.responses import ChatResponse
from ai_chatbot.services.rate_limiter import rate_limiter_service
import uuid


class ChatRequest(BaseModel):
    """
    Request model for chat endpoint
    """
    message: str
    conversation_id: str = None


router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["chatbot"])
def chat_with_ai_assistant(
    chat_request: ChatRequest,
    current_user_id: uuid.UUID = Depends(auth_validator.get_current_user_id)
):
    """
    Chat with the AI assistant to manage tasks using natural language.

    This endpoint processes natural language commands from the user and translates
    them into appropriate task operations using the AI chatbot orchestration system.
    """
    # Apply rate limiting
    if not rate_limiter_service.check_user_rate_limit(str(current_user_id), 'chat_message'):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please slow down your requests."
        )

    try:
        # Validate the request
        if not chat_request.message or not chat_request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )

        # Process the chat message through the workflow
        response = chat_processing_workflow.process_chat_message(
            user_message=chat_request.message,
            user_id=str(current_user_id),
            auth_token="",  # The auth token would typically come from the headers, but it's validated by the dependency
            conversation_id=chat_request.conversation_id
        )

        # Log the interaction
        logger.info(
            f"Chat interaction processed",
            user_id=str(current_user_id),
            conversation_id=response.conversation_id,
            message_length=len(chat_request.message)
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}",
                     user_id=str(current_user_id),
                     message=chat_request.message)

        # Return a user-friendly error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )


# Additional endpoint for handling confirmation responses
@router.post("/chat/confirm", response_model=ChatResponse, tags=["chatbot"])
def confirm_chat_action(
    chat_request: ChatRequest,
    current_user_id: uuid.UUID = Depends(auth_validator.get_current_user_id)
):
    """
    Handle confirmation responses for actions that require user confirmation.

    This endpoint is used when the AI chatbot needs to confirm potentially
    destructive actions with the user before proceeding.
    """
    # Apply rate limiting for confirmation actions
    if not rate_limiter_service.check_user_rate_limit(str(current_user_id), 'chat_message'):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please slow down your requests."
        )

    try:
        # Validate the request
        if not chat_request.message or not chat_request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmation message cannot be empty"
            )

        if not chat_request.conversation_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversation ID is required for confirmation"
            )

        # Handle the confirmation response
        response = chat_processing_workflow.handle_confirmation_response(
            user_response=chat_request.message,
            user_id=str(current_user_id),
            auth_token="",  # The auth token would typically come from the headers, but it's validated by the dependency
            conversation_id=chat_request.conversation_id
        )

        # Log the confirmation interaction
        logger.info(
            f"Confirmation response processed",
            user_id=str(current_user_id),
            conversation_id=chat_request.conversation_id,
            message_length=len(chat_request.message)
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in confirmation endpoint: {str(e)}",
                     user_id=str(current_user_id),
                     conversation_id=chat_request.conversation_id,
                     message=chat_request.message)

        # Return a user-friendly error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your confirmation"
        )


# Endpoint to start a new conversation
@router.post("/chat/start", response_model=ChatResponse, tags=["chatbot"])
def start_new_conversation(
    current_user_id: uuid.UUID = Depends(auth_validator.get_current_user_id)
):
    """
    Start a new conversation with the AI assistant.

    This endpoint creates a new conversation and returns the conversation ID
    that can be used for subsequent messages in the same conversation.
    """
    # Apply rate limiting for new conversations
    if not rate_limiter_service.check_user_rate_limit(str(current_user_id), 'conversations_per_day'):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum number of conversations per day reached."
        )

    try:
        # Create a new conversation by getting a new conversation ID
        from ai_chatbot.services.conversation_state import conversation_state_manager
        conversation_id = conversation_state_manager.create_conversation(str(current_user_id))

        # Create a welcome response
        welcome_response = ChatResponse(
            conversation_id=conversation_id,
            response="Hello! I'm your AI assistant. How can I help you manage your tasks today?",
            intent="welcome",
            entities={},
            suggestions=[
                "Add a task: Buy groceries",
                "Show my tasks",
                "Mark a task as complete"
            ]
        )

        # Log the new conversation start
        logger.info(
            f"New conversation started",
            user_id=str(current_user_id),
            conversation_id=conversation_id
        )

        return welcome_response

    except Exception as e:
        logger.error(f"Error starting new conversation: {str(e)}",
                     user_id=str(current_user_id))

        # Return a user-friendly error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while starting a new conversation"
        )