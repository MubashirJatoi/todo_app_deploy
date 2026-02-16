from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None  # For maintaining conversation context


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    messages: List[ChatMessage]


class TaskOperationRequest(BaseModel):
    operation: str  # "create", "update", "delete", "search", "list"
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    due_date: Optional[str] = None
    task_id: Optional[str] = None  # For update/delete operations


class TaskOperationResponse(BaseModel):
    success: bool
    message: str
    task_data: Optional[dict] = None