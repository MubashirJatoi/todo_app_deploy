from typing import Dict, Optional
from ai_chatbot.services.auth_validator import auth_validator
from ai_chatbot.utils.logging import logger
import uuid


class UserAuthValidator:
    """
    Validator for user authentication and authorization in the AI chatbot
    """

    def __init__(self):
        self.auth_validator = auth_validator

    def validate_user_token(self, auth_token: str) -> Optional[uuid.UUID]:
        """
        Validate the user's authentication token and return user ID if valid
        """
        try:
            user_id = self.auth_validator.validate_token(auth_token)
            return user_id
        except Exception as e:
            logger.error(f"Error validating user token: {str(e)}")
            return None

    def validate_user_access(self, user_id: uuid.UUID, requested_resource: str, requested_action: str) -> bool:
        """
        Validate if the user has access to perform the requested action on the resource
        """
        try:
            # In a real implementation, you would check permissions against policies
            # For now, we'll implement basic checks

            # Users can only access their own resources
            if requested_resource.startswith("task:") or requested_resource == "tasks":
                # This check would typically be done by verifying the user_id matches
                # the owner of the task, but the actual check happens in the Phase 2 API
                return True

            # Add more resource types as needed
            return False
        except Exception as e:
            logger.error(f"Error validating user access: {str(e)}",
                         user_id=str(user_id),
                         resource=requested_resource,
                         action=requested_action)
            return False

    def is_user_authenticated(self, auth_token: str) -> bool:
        """
        Check if the user is authenticated with a valid token
        """
        try:
            user_id = self.validate_user_token(auth_token)
            return user_id is not None
        except Exception as e:
            logger.error(f"Error checking user authentication: {str(e)}")
            return False

    def validate_user_owns_resource(self, user_id: uuid.UUID, resource_owner_id: uuid.UUID) -> bool:
        """
        Validate that the user owns the resource they're trying to access
        """
        try:
            # Compare the authenticated user's ID with the resource owner's ID
            return str(user_id) == str(resource_owner_id)
        except Exception as e:
            logger.error(f"Error validating resource ownership: {str(e)}",
                         user_id=str(user_id),
                         resource_owner_id=str(resource_owner_id))
            return False


# Global instance for reuse
user_auth_validator = UserAuthValidator()