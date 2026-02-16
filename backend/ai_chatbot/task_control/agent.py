from typing import Dict, Optional
from ai_chatbot.models.command import NaturalLanguageCommand, ProcessedCommandResult, IntentType
from ai_chatbot.task_control.create_handler import create_task_handler
from ai_chatbot.task_control.update_handler import update_task_handler
from ai_chatbot.task_control.delete_handler import delete_task_handler
from ai_chatbot.task_control.list_handler import list_tasks_handler
from ai_chatbot.task_control.search_handler import search_tasks_handler
from ai_chatbot.task_control.user_info_handler import user_info_handler
from ai_chatbot.utils.logging import logger


class TaskControlAgent:
    """
    Agent responsible for handling task-related operations based on user commands
    """

    def __init__(self):
        self.create_handler = create_task_handler
        self.update_handler = update_task_handler
        self.delete_handler = delete_task_handler
        self.list_handler = list_tasks_handler
        self.search_handler = search_tasks_handler

    def execute_command(self, command: NaturalLanguageCommand, auth_token: str) -> ProcessedCommandResult:
        """
        Execute the appropriate task operation based on the command intent
        """
        try:
            intent = command.intent
            entities = command.entities
            user_id = command.user_id

            logger.info(
                f"Executing task command: {intent}",
                user_id=str(user_id) if user_id else None,
                intent=intent,
                entities=entities
            )

            if intent == IntentType.CREATE_TASK:
                return self.create_handler.handle(command, auth_token)
            elif intent == IntentType.UPDATE_TASK:
                return self.update_handler.handle(command, auth_token)
            elif intent == IntentType.COMPLETE_TASK:
                return self.update_handler.handle_completion(command, auth_token)
            elif intent == IntentType.DELETE_TASK:
                return self.delete_handler.handle(command, auth_token)
            elif intent == IntentType.LIST_TASKS:
                return self.list_handler.handle(command, auth_token)
            elif intent == IntentType.SEARCH_TASKS:
                return self.search_handler.handle(command, auth_token)
            elif intent == IntentType.GET_USER_INFO:
                # Use the user info handler to get user information
                return user_info_handler.handle(command, auth_token)
            else:
                return ProcessedCommandResult(
                    success=False,
                    message=f"Unknown or unsupported intent: {intent}",
                    intent=intent,
                    entities=entities
                )

        except Exception as e:
            logger.error(f"Error executing task command: {str(e)}", command=command.dict())
            return ProcessedCommandResult(
                success=False,
                message=f"Error executing task: {str(e)}",
                intent=command.intent,
                entities=command.entities,
                follow_up_required=False
            )

    def validate_task_operation(self, command: NaturalLanguageCommand) -> bool:
        """
        Validate if the task operation is allowed based on command and user context
        """
        try:
            # Basic validation
            if not command.user_id:
                return False

            # Check if command has required entities for the intent
            if command.intent == IntentType.CREATE_TASK:
                # Creation might be allowed with minimal info
                return True
            elif command.intent in [IntentType.UPDATE_TASK, IntentType.COMPLETE_TASK, IntentType.DELETE_TASK]:
                # These require some way to identify the task
                return 'task_title' in command.entities or 'search_term' in command.entities
            elif command.intent in [IntentType.LIST_TASKS, IntentType.SEARCH_TASKS]:
                # These are generally allowed
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error validating task operation: {str(e)}", command=command.dict())
            return False


# Global instance for reuse
task_control_agent = TaskControlAgent()