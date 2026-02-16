from typing import Dict, Optional
from ai_chatbot.models.command import NaturalLanguageCommand, ProcessedCommandResult, IntentType
from ai_chatbot.services.phase2_client import phase2_client
from ai_chatbot.utils.logging import logger


class UserInfoHandler:
    """
    Handler for retrieving user information based on natural language input
    """

    def handle(self, command: NaturalLanguageCommand, auth_token: str) -> ProcessedCommandResult:
        """
        Handle user info command
        """
        try:
            user_id = command.user_id
            entities = command.entities

            # Call Phase 2 API to get user information
            user_info = phase2_client.get_user_info(str(user_id), auth_token)

            if not user_info:
                return ProcessedCommandResult(
                    success=False,
                    message="Sorry, I couldn't retrieve your user information.",
                    intent=command.intent,
                    entities=entities,
                    follow_up_required=True
                )

            # Extract requested information based on entities or raw input
            requested_info = entities.get('info_type', '').lower()

            # Format response based on requested information
            if requested_info == 'email':
                info_value = user_info.get('email', 'email not found')
                message = f"Your email address is {info_value}."
            elif requested_info == 'name':
                info_value = user_info.get('name', user_info.get('full_name', 'name not found'))
                message = f"Your name is {info_value}."
            elif requested_info == 'id' or requested_info == 'user_id':
                message = f"Your user ID is {user_id}."
            else:
                # Return general user info
                email = user_info.get('email', 'not available')
                name = user_info.get('name', user_info.get('full_name', 'not available'))

                if name != 'not available' and email != 'not available':
                    message = f"You are logged in as {name} with email {email}."
                elif email != 'not available':
                    message = f"You are logged in with email {email}."
                elif name != 'not available':
                    message = f"You are logged in as {name}."
                else:
                    message = f"You are logged in with user ID {user_id}."

            logger.log_task_operation(
                user_id=str(user_id),
                operation="GET_USER_INFO",
                success=True,
                details={"requested_info": requested_info, "user_info_keys": list(user_info.keys()) if user_info else []}
            )

            return ProcessedCommandResult(
                success=True,
                message=message,
                intent=command.intent,
                entities=entities,
                user_context=user_info,
                suggestions=[
                    "Show me my tasks",
                    "What can I do with this app?",
                    "How do I add a new task?"
                ]
            )

        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}", command=command.dict())
            return ProcessedCommandResult(
                success=False,
                message=f"Sorry, I couldn't retrieve your user information: {str(e)}",
                intent=command.intent,
                entities=entities,
                follow_up_required=True
            )


# Global instance for reuse
user_info_handler = UserInfoHandler()