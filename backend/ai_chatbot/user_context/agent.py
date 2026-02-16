from typing import Dict, Optional
from ai_chatbot.services.auth_validator import auth_validator
from ai_chatbot.utils.logging import logger
from sqlmodel import Session, select
from models import User
from db import engine


class UserContextAgent:
    """
    Agent responsible for managing user context and authentication
    """

    def __init__(self):
        self.auth_validator = auth_validator

    def get_user_info(self, auth_token: str) -> Optional[Dict]:
        """
        Get user information from the authentication token
        """
        try:
            user_id = self.auth_validator.validate_token(auth_token)
            if user_id:
                # Fetch user details from the database
                user_details = self._get_user_from_db(user_id)

                if user_details:
                    return {
                        "user_id": str(user_id),
                        "email": user_details.email,
                        "name": user_details.name,
                        "authenticated": True,
                        "permissions": ["read_tasks", "write_tasks", "delete_tasks"]
                    }
                else:
                    return {
                        "authenticated": False,
                        "error": "User not found in database"
                    }
            else:
                return {
                    "authenticated": False,
                    "error": "Invalid token"
                }
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return {
                "authenticated": False,
                "error": str(e)
            }

    def _get_user_from_db(self, user_id: str) -> Optional[User]:
        """
        Fetch user from database by user ID
        """
        try:
            with Session(engine) as session:
                statement = select(User).where(User.id == user_id)
                user = session.exec(statement).first()
                return user
        except Exception as e:
            logger.error(f"Error fetching user from database: {str(e)}", user_id=user_id)
            return None

    def validate_user_access(self, user_id: str, resource: str, action: str) -> bool:
        """
        Validate if the user has access to perform an action on a resource
        """
        try:
            # In a real implementation, you would check user permissions against a policy
            # For now, assume all authenticated users can access their own tasks
            if resource.startswith("task:") or resource == "tasks":
                # User can only access resources that belong to them
                # This is handled by the Phase 2 API, but we can add additional checks here
                return True
            else:
                # Unknown resource type
                return False
        except Exception as e:
            logger.error(f"Error validating user access: {str(e)}", user_id=user_id, resource=resource, action=action)
            return False

    def get_user_permissions(self, user_id: str) -> Dict[str, bool]:
        """
        Get the permissions for a specific user
        """
        try:
            # In a real implementation, you would fetch permissions from a database or policy engine
            # For now, return default permissions for a regular user
            return {
                "can_create_tasks": True,
                "can_read_tasks": True,
                "can_update_tasks": True,
                "can_delete_tasks": True,
                "can_search_tasks": True,
                "can_manage_account": True
            }
        except Exception as e:
            logger.error(f"Error getting user permissions: {str(e)}", user_id=user_id)
            return {}

    def update_user_context(self, user_id: str, context_data: Dict) -> bool:
        """
        Update user context data (e.g., preferences, settings)
        """
        try:
            # In a real implementation, you would store user context in a database
            # For now, just log the update
            logger.info(f"User context updated", user_id=user_id, context_data=context_data)
            return True
        except Exception as e:
            logger.error(f"Error updating user context: {str(e)}", user_id=user_id, context_data=context_data)
            return False

    def get_user_context(self, user_id: str) -> Dict:
        """
        Get user context data
        """
        try:
            # In a real implementation, you would fetch user context from a database
            # For now, return default context
            return {
                "preferences": {
                    "default_priority": "medium",
                    "notifications_enabled": True,
                    "theme": "light"
                },
                "settings": {
                    "language": "en",
                    "timezone": "UTC"
                },
                "recent_activities": []
            }
        except Exception as e:
            logger.error(f"Error getting user context: {str(e)}", user_id=user_id)
            return {}


# Global instance for reuse
user_context_agent = UserContextAgent()