"""
API endpoints for handling confirmation requests
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import uuid

from ..models.responses import ChatResponse, ConfirmationResponse
from ..models.command import NaturalLanguageCommand, IntentType, ProcessedCommandResult
from ..services.confirmation_service import confirmation_service
from ..services.auth_validator import validate_auth_token
from ..utils.logging import logger


router = APIRouter()
security = HTTPBearer()


class ConfirmationActionRequest:
    """Request model for confirmation actions"""
    def __init__(self, confirmation_id: str, action: str = "confirm"):
        self.confirmation_id = confirmation_id
        self.action = action  # "confirm" or "reject"


@router.post("/confirm", response_model=ChatResponse)
async def confirm_action(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    POST endpoint to handle confirmation of actions that require user approval
    """
    try:
        auth_token = credentials.credentials

        # Validate the authentication token
        user_id = await validate_auth_token(auth_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

        # Parse request body
        body = await request.json()
        confirmation_id = body.get("confirmation_id")
        action = body.get("action", "confirm")  # Default to confirm

        if not confirmation_id:
            raise HTTPException(status_code=400, detail="confirmation_id is required")

        # Log the confirmation request
        logger.log_api_call(
            endpoint="/api/confirm",
            user_id=str(user_id),
            request_data={"confirmation_id": confirmation_id, "action": action},
            response_data={}
        )

        # Process the confirmation based on the action
        if action.lower() == "confirm":
            # Attempt to confirm the action
            success = confirmation_service.confirm_action(confirmation_id)

            if not success:
                raise HTTPException(status_code=400, detail="Invalid or expired confirmation ID")

            # Process the confirmed action
            result = confirmation_service.process_confirmed_action(confirmation_id)

            if result:
                # Log the successful operation
                logger.log_task_operation(
                    user_id=str(user_id),
                    operation="CONFIRM_ACTION_PROCESSED",
                    success=True,
                    details={"confirmation_id": confirmation_id, "action_result": result.message}
                )

                return ChatResponse(
                    conversation_id=str(uuid.uuid4()),
                    message=result.message,
                    success=result.success,
                    intent=result.intent.value if result.intent else None,
                    suggestions=result.suggestions or [],
                    follow_up_required=False
                )
            else:
                raise HTTPException(status_code=400, detail="Failed to process confirmed action")

        elif action.lower() == "reject":
            # Reject the action
            success = confirmation_service.reject_action(confirmation_id)

            if not success:
                raise HTTPException(status_code=400, detail="Invalid or expired confirmation ID")

            # Log the rejection
            logger.log_task_operation(
                user_id=str(user_id),
                operation="CONFIRM_ACTION_REJECTED",
                success=True,
                details={"confirmation_id": confirmation_id, "action": "rejected"}
            )

            return ChatResponse(
                conversation_id=str(uuid.uuid4()),
                message="Action has been cancelled as requested.",
                success=True,
                intent=IntentType.CANCELLED.value,
                suggestions=[
                    "What else can I help you with?",
                    "Show me my tasks",
                    "Add a new task"
                ],
                follow_up_required=False
            )

        else:
            raise HTTPException(status_code=400, detail="Action must be either 'confirm' or 'reject'")

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in /confirm endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while processing confirmation")


@router.post("/confirm-status", response_model=ConfirmationResponse)
async def get_confirmation_status(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    POST endpoint to check the status of a confirmation request
    """
    try:
        auth_token = credentials.credentials

        # Validate the authentication token
        user_id = await validate_auth_token(auth_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

        # Parse request body
        body = await request.json()
        confirmation_id = body.get("confirmation_id")

        if not confirmation_id:
            raise HTTPException(status_code=400, detail="confirmation_id is required")

        # Get confirmation status
        confirmation = confirmation_service.get_confirmation_status(confirmation_id)

        if confirmation is None:
            raise HTTPException(status_code=404, detail="Confirmation not found or expired")

        # Log the status check
        logger.log_api_call(
            endpoint="/api/confirm-status",
            user_id=str(user_id),
            request_data={"confirmation_id": confirmation_id},
            response_data={"status": "found", "confirmed": confirmation.is_confirmed, "rejected": confirmation.is_rejected}
        )

        return ConfirmationResponse(
            confirmation_id=confirmation.confirmation_id,
            message=confirmation.message,
            is_confirmed=confirmation.is_confirmed,
            is_rejected=confirmation.is_rejected,
            is_expired=confirmation_service.is_expired(confirmation),
            action_to_confirm=confirmation.action_to_confirm,
            suggestions=[
                "Confirm this action",
                "Reject this action",
                "Tell me more about this action"
            ]
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in /confirm-status endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while checking confirmation status")


# Additional helper endpoint to initiate confirmations (useful for testing)
@router.post("/request-confirmation", response_model=ConfirmationResponse)
async def request_confirmation(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    POST endpoint to request a new confirmation for testing purposes
    """
    try:
        auth_token = credentials.credentials

        # Validate the authentication token
        user_id = await validate_auth_token(auth_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

        # Parse request body
        body = await request.json()
        action_to_confirm = body.get("action_to_confirm", "perform this action")
        message = body.get("message", f"Are you sure you want to {action_to_confirm}?")

        # Create a mock command for the confirmation
        mock_command = NaturalLanguageCommand(
            raw_input=f"confirm {action_to_confirm}",
            intent=IntentType.DELETE_TASK,  # Using DELETE_TASK as example intent
            entities={},
            user_id=user_id
        )

        # Create confirmation request
        confirmation_request = confirmation_service.create_confirmation_request(
            command=mock_command,
            action_to_confirm=action_to_confirm,
            custom_message=message
        )

        # Log the request
        logger.log_api_call(
            endpoint="/api/request-confirmation",
            user_id=str(user_id),
            request_data={"action_to_confirm": action_to_confirm},
            response_data={"confirmation_id": confirmation_request.confirmation_id}
        )

        return ConfirmationResponse(
            confirmation_id=confirmation_request.confirmation_id,
            message=confirmation_request.message,
            is_confirmed=confirmation_request.is_confirmed,
            is_rejected=confirmation_request.is_rejected,
            is_expired=confirmation_service.is_expired(confirmation_request),
            action_to_confirm=confirmation_request.action_to_confirm,
            suggestions=[
                "Confirm this action",
                "Reject this action"
            ]
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in /request-confirmation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while requesting confirmation")