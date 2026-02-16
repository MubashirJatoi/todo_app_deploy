from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import uuid

from ai_chatbot.models.responses import ChatResponse, UserInfoResponse
from ai_chatbot.models.command import NaturalLanguageCommand, IntentType
from ai_chatbot.task_control.user_info_handler import user_info_handler
from ai_chatbot.services.auth_validator import validate_auth_token
from ai_chatbot.utils.logging import logger

router = APIRouter()
security = HTTPBearer()


@router.get("/user-info", response_model=UserInfoResponse)
async def get_user_info(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    GET endpoint to retrieve user information
    """
    try:
        auth_token = credentials.credentials

        # Validate the authentication token
        user_id = await validate_auth_token(auth_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

        # Create a command for getting user info
        command = NaturalLanguageCommand(
            raw_input="get user info",
            intent=IntentType.GET_USER_INFO,
            entities={},
            user_id=user_id
        )

        # Process the command using the user info handler
        result = user_info_handler.handle(command, auth_token)

        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)

        # Log the successful operation
        logger.log_api_call(
            endpoint="/api/user-info",
            user_id=str(user_id),
            request_data={"intent": "GET_USER_INFO"},
            response_data={"success": True, "user_info_available": bool(result.user_context)}
        )

        # Return the user info response
        return UserInfoResponse(
            conversation_id=str(uuid.uuid4()),
            user_info=result.user_context or {},
            message=result.message,
            suggestions=result.suggestions or []
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in /user-info endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving user info")


@router.get("/user-info/{info_type}", response_model=UserInfoResponse)
async def get_specific_user_info(info_type: str, request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    GET endpoint to retrieve specific type of user information (email, name, etc.)
    """
    try:
        auth_token = credentials.credentials

        # Validate the authentication token
        user_id = await validate_auth_token(auth_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

        # Create a command for getting specific user info
        command = NaturalLanguageCommand(
            raw_input=f"get user {info_type}",
            intent=IntentType.GET_USER_INFO,
            entities={"info_type": info_type},
            user_id=user_id
        )

        # Process the command using the user info handler
        result = user_info_handler.handle(command, auth_token)

        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)

        # Log the successful operation
        logger.log_api_call(
            endpoint=f"/api/user-info/{info_type}",
            user_id=str(user_id),
            request_data={"intent": "GET_USER_INFO", "info_type": info_type},
            response_data={"success": True, "user_info_available": bool(result.user_context)}
        )

        # Return the user info response
        return UserInfoResponse(
            conversation_id=str(uuid.uuid4()),
            user_info=result.user_context or {},
            message=result.message,
            suggestions=result.suggestions or []
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in /user-info/{info_type} endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving user info")