from pydantic import BaseModel
from typing import Dict, List, Optional
from enum import Enum
import uuid


class IntentType(str, Enum):
    CREATE_TASK = "CREATE_TASK"
    UPDATE_TASK = "UPDATE_TASK"
    DELETE_TASK = "DELETE_TASK"
    LIST_TASKS = "LIST_TASKS"
    SEARCH_TASKS = "SEARCH_TASKS"
    FILTER_TASKS = "FILTER_TASKS"
    COMPLETE_TASK = "COMPLETE_TASK"
    GET_USER_INFO = "GET_USER_INFO"
    UNKNOWN = "UNKNOWN"


class NaturalLanguageCommand(BaseModel):
    """
    Model representing a natural language command from the user
    """
    raw_input: str
    intent: IntentType
    entities: Dict[str, str] = {}
    confidence: float = 0.0
    user_id: Optional[uuid.UUID] = None
    conversation_id: Optional[str] = None
    timestamp: Optional[str] = None
    suggestions: Optional[List[str]] = None

    class Config:
        use_enum_values = True  # Use string values of enums


class ProcessedCommandResult(BaseModel):
    """
    Model representing the result of processing a natural language command
    """
    success: bool
    message: str
    intent: IntentType
    entities: Dict[str, str] = {}
    task_result: Optional[Dict] = None
    user_context: Optional[Dict] = None
    suggestions: Optional[List[str]] = None
    follow_up_required: bool = False