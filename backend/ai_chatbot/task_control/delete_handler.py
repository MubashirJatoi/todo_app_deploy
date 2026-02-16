from typing import Dict, Optional
from ai_chatbot.models.command import NaturalLanguageCommand, ProcessedCommandResult, IntentType
from ai_chatbot.services.phase2_client import phase2_client
from ai_chatbot.utils.logging import logger


class DeleteTaskHandler:
    """
    Handler for deleting tasks based on natural language input
    """

    def handle(self, command: NaturalLanguageCommand, auth_token: str) -> ProcessedCommandResult:
        """
        Handle delete task command
        """
        try:
            user_id = command.user_id
            entities = command.entities

            # Find the task to delete
            task_id = entities.get('task_id')
            search_term = entities.get('search_term') or entities.get('task_title')

            if not search_term and not task_id:
                return ProcessedCommandResult(
                    success=False,
                    message="No task specified to delete. Please specify which task you want to delete.",
                    intent=command.intent,
                    entities=entities,
                    follow_up_required=True
                )

            # If no specific task ID, search for the task
            if not task_id:
                tasks = phase2_client.get_user_tasks(str(user_id), auth_token, {"search": search_term})
                if not tasks:
                    return ProcessedCommandResult(
                        success=False,
                        message=f"I couldn't find any tasks containing '{search_term}'.",
                        intent=command.intent,
                        entities=entities,
                        follow_up_required=True
                    )

                # Use the first matching task
                task_to_delete = tasks[0]
                task_id = task_to_delete.get('id')

            # Before deleting, get the task details to confirm
            task_details = phase2_client.get_task_by_id(str(user_id), auth_token, task_id)

            if not task_details:
                return ProcessedCommandResult(
                    success=False,
                    message="The task you're trying to delete doesn't exist or you don't have permission to access it.",
                    intent=command.intent,
                    entities=entities,
                    follow_up_required=False
                )

            # Call Phase 2 API to delete the task
            success = phase2_client.delete_task(str(user_id), auth_token, task_id)

            if success:
                logger.log_task_operation(
                    user_id=str(user_id),
                    operation="DELETE_TASK",
                    success=True,
                    details={"task_id": task_id, "task_title": task_details.get('title')}
                )

                return ProcessedCommandResult(
                    success=True,
                    message=f"I've deleted the task: '{task_details.get('title', 'Unknown')}'",
                    intent=command.intent,
                    entities=entities,
                    suggestions=[
                        "Show me all my tasks",
                        "Add a new task"
                    ]
                )
            else:
                return ProcessedCommandResult(
                    success=False,
                    message=f"Sorry, I couldn't delete the task: '{task_details.get('title', 'Unknown')}'",
                    intent=command.intent,
                    entities=entities,
                    follow_up_required=True
                )

        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}", command=command.dict())
            return ProcessedCommandResult(
                success=False,
                message=f"Sorry, I couldn't delete the task: {str(e)}",
                intent=command.intent,
                entities=entities,
                follow_up_required=True
            )

    def handle_with_confirmation(self, command: NaturalLanguageCommand, auth_token: str) -> ProcessedCommandResult:
        """
        Handle delete task command with confirmation step
        """
        try:
            user_id = command.user_id
            entities = command.entities

            # Find the task to delete
            task_id = entities.get('task_id')
            search_term = entities.get('search_term') or entities.get('task_title')

            if not search_term and not task_id:
                return ProcessedCommandResult(
                    success=False,
                    message="No task specified to delete. Please specify which task you want to delete.",
                    intent=command.intent,
                    entities=entities,
                    follow_up_required=True
                )

            # If no specific task ID, search for the task
            if not task_id:
                tasks = phase2_client.get_user_tasks(str(user_id), auth_token, {"search": search_term})
                if not tasks:
                    return ProcessedCommandResult(
                        success=False,
                        message=f"I couldn't find any tasks containing '{search_term}'.",
                        intent=command.intent,
                        entities=entities,
                        follow_up_required=True
                    )

                # Use the first matching task
                task_to_delete = tasks[0]
                task_id = task_to_delete.get('id')

            # Get the task details to confirm
            task_details = phase2_client.get_task_by_id(str(user_id), auth_token, task_id)

            if not task_details:
                return ProcessedCommandResult(
                    success=False,
                    message="The task you're trying to delete doesn't exist or you don't have permission to access it.",
                    intent=command.intent,
                    entities=entities,
                    follow_up_required=False
                )

            # Instead of deleting immediately, return a confirmation request
            return ProcessedCommandResult(
                success=True,
                message=f"Are you sure you want to delete the task '{task_details.get('title', 'Unknown')}'? Please confirm.",
                intent=command.intent,
                entities=entities,
                follow_up_required=True  # Indicates that further action is needed
            )

        except Exception as e:
            logger.error(f"Error preparing task deletion with confirmation: {str(e)}", command=command.dict())
            return ProcessedCommandResult(
                success=False,
                message=f"Sorry, I couldn't prepare the task for deletion: {str(e)}",
                intent=command.intent,
                entities=entities,
                follow_up_required=True
            )


# Global instance for reuse
delete_task_handler = DeleteTaskHandler()