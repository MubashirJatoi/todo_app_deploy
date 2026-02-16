import uuid
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta


class ConversationState:
    """
    Manages conversation state for the AI chatbot
    """

    # Conversation states
    STATE_ACTIVE = "ACTIVE"
    STATE_AWAITING_CLARIFICATION = "AWAITING_CLARIFICATION"
    STATE_CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"
    STATE_IN_PROGRESS = "IN_PROGRESS"
    STATE_COMPLETED = "COMPLETED"
    STATE_ERROR = "ERROR"

    def __init__(self):
        # In-memory storage for conversation states
        # In a production environment, this would use Redis or database
        self.conversations: Dict[str, Dict[str, Any]] = {}

    def create_conversation(self, user_id: str) -> str:
        """
        Create a new conversation and return the conversation ID
        """
        conversation_id = str(uuid.uuid4())

        self.conversations[conversation_id] = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_updated": datetime.now(),
            "state": self.STATE_ACTIVE,
            "messages": [],
            "context": {},
            "pending_action": None,
            "expires_at": datetime.now() + timedelta(hours=24)  # Expires in 24 hours
        }

        return conversation_id

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation state by ID
        """
        if conversation_id in self.conversations:
            # Check if conversation has expired
            if datetime.now() > self.conversations[conversation_id]["expires_at"]:
                self.end_conversation(conversation_id)
                return None

            return self.conversations[conversation_id]

        return None

    def update_conversation_state(self, conversation_id: str, new_state: str) -> bool:
        """
        Update the state of a conversation
        """
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["state"] = new_state
            self.conversations[conversation_id]["last_updated"] = datetime.now()
            return True
        return False

    def add_message(self, conversation_id: str, role: str, content: str) -> bool:
        """
        Add a message to the conversation
        """
        if conversation_id in self.conversations:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now()
            }

            self.conversations[conversation_id]["messages"].append(message)
            self.conversations[conversation_id]["last_updated"] = datetime.now()
            return True
        return False

    def set_pending_action(self, conversation_id: str, action: Dict[str, Any]) -> bool:
        """
        Set a pending action for the conversation
        """
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["pending_action"] = action
            self.conversations[conversation_id]["last_updated"] = datetime.now()
            return True
        return False

    def get_pending_action(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the pending action for the conversation
        """
        if conversation_id in self.conversations:
            return self.conversations[conversation_id].get("pending_action")
        return None

    def clear_pending_action(self, conversation_id: str) -> bool:
        """
        Clear the pending action for the conversation
        """
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["pending_action"] = None
            self.conversations[conversation_id]["last_updated"] = datetime.now()
            return True
        return False

    def update_context(self, conversation_id: str, key: str, value: Any) -> bool:
        """
        Update context information for the conversation
        """
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["context"][key] = value
            self.conversations[conversation_id]["last_updated"] = datetime.now()
            return True
        return False

    def get_context(self, conversation_id: str, key: str, default: Any = None) -> Any:
        """
        Get context information for the conversation
        """
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]["context"].get(key, default)
        return default

    def end_conversation(self, conversation_id: str) -> bool:
        """
        End a conversation by removing it from memory
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False

    def cleanup_expired_conversations(self) -> int:
        """
        Remove expired conversations and return count of removed conversations
        """
        current_time = datetime.now()
        expired_ids = []

        for conv_id, conv_data in self.conversations.items():
            if current_time > conv_data["expires_at"]:
                expired_ids.append(conv_id)

        for conv_id in expired_ids:
            del self.conversations[conv_id]

        return len(expired_ids)


# Global instance for reuse
conversation_state_manager = ConversationState()