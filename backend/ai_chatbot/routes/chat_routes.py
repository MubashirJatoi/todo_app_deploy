from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
import uuid
from auth import get_current_user_id
from db import get_session
from sqlmodel import Session
from ai_chatbot.models.chat_models import ChatRequest, ChatResponse, ChatMessage, TaskOperationRequest, TaskOperationResponse
from ai_chatbot.services.chat_service import ChatbotService
from datetime import datetime


router = APIRouter()
chat_service = ChatbotService()


@router.post("/chat", tags=["chatbot"])
def chat_with_bot(
    chat_request: ChatRequest,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Chat with the AI bot to manage your tasks using natural language.
    """
    try:
        # Process the user's message using the chatbot service with user context
        response_text = chat_service.process_message(chat_request.message, session, current_user_id)

        # Generate a conversation ID if not provided
        conversation_id = chat_request.conversation_id or str(uuid.uuid4())

        # Create chat messages
        user_message = ChatMessage(
            role="user",
            content=chat_request.message,
            timestamp=datetime.now()
        )

        assistant_message = ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=datetime.now()
        )

        chat_response = ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            messages=[user_message, assistant_message]
        )

        return chat_response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post("/task-operation", tags=["chatbot"])
def perform_task_operation(
    task_operation: TaskOperationRequest,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Perform a task operation based on natural language input.
    This endpoint translates natural language into specific task operations.
    """
    try:
        # This would typically call the appropriate task service methods
        # based on the operation type and user ID

        if task_operation.operation == "create":
            # Would call create_task_for_user from services/task_service.py
            message = f"Creating task: {task_operation.title}"
        elif task_operation.operation == "update":
            # Would call update_task_for_user from services/task_service.py
            message = f"Updating task: {task_operation.title or task_operation.task_id}"
        elif task_operation.operation == "delete":
            # Would call delete_task_for_user from services/task_service.py
            message = f"Deleting task: {task_operation.title or task_operation.task_id}"
        elif task_operation.operation == "search":
            # Would call get_tasks_by_user from services/task_service.py with filters
            message = f"Searching for tasks: {task_operation.title}"
        else:
            message = f"Unknown operation: {task_operation.operation}"

        return TaskOperationResponse(
            success=True,
            message=message,
            task_data={
                "operation": task_operation.operation,
                "user_id": str(current_user_id)
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing task operation: {str(e)}"
        )