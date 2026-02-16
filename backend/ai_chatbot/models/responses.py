from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class BaseResponse(BaseModel):
    """
    Base response model for all AI chatbot API responses
    """
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()


class ErrorResponse(BaseModel):
    """
    Error response model
    """
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()


class ChatResponse(BaseModel):
    """
    Response model for chat interactions
    """
    conversation_id: str
    response: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    timestamp: datetime = datetime.now()


class TaskOperationResponse(BaseModel):
    """
    Response model for task operations
    """
    operation: str
    success: bool
    message: str
    task_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()


class UserInfoResponse(BaseModel):
    """
    Response model for user information requests
    """
    conversation_id: str
    user_info: Optional[Dict[str, Any]] = None
    message: str
    suggestions: Optional[List[str]] = None
    timestamp: datetime = datetime.now()


class UserContextResponse(BaseModel):
    """
    Response model for user context information
    """
    user_id: uuid.UUID
    authenticated: bool
    user_info: Optional[Dict[str, Any]] = None
    permissions: List[str] = []
    timestamp: datetime = datetime.now()


class ConfirmationResponse(BaseModel):
    """
    Response model for confirmation requests
    """
    confirmation_id: str
    message: str
    is_confirmed: bool
    is_rejected: bool
    is_expired: bool
    action_to_confirm: str
    suggestions: Optional[List[str]] = None
    timestamp: datetime = datetime.now()