from typing import Dict, Optional
from ai_chatbot.models.command import NaturalLanguageCommand, ProcessedCommandResult, IntentType
from ai_chatbot.services.phase2_client import phase2_client
from ai_chatbot.utils.logging import logger
import re


class UpdateTaskHandler:
    """
    Handler for updating tasks based on natural language input
    """

    def handle(self, command: NaturalLanguageCommand, auth_token: str) -> ProcessedCommandResult:
        """
        Handle update task command
        """
        try:
            user_id = command.user_id
            entities = command.entities

            # Find the task to update
            task_id = entities.get('task_id')
            search_term = entities.get('search_term') or entities.get('task_title')

            if not search_term and not task_id:
                return ProcessedCommandResult(
                    success=False,
                    message="No task specified to update. Please specify which task you want to update.",
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
                task_to_update = tasks[0]
                task_id = task_to_update.get('id')

            # Prepare update data based on entities
            update_data = {}

            # Check for various update properties in entities
            if 'title' in entities:
                update_data['title'] = entities['title']
            if 'description' in entities:
                update_data['description'] = entities['description']
            if 'priority' in entities:
                update_data['priority'] = entities['priority']
            if 'due_date' in entities:
                update_data['due_date'] = entities['due_date']
            if 'category' in entities:
                update_data['category'] = entities['category']

            # If no specific update fields were provided, ask for clarification
            if not update_data:
                return ProcessedCommandResult(
                    success=False,
                    message=f"What would you like to update about the task '{search_term or task_id}'? You can update title, description, priority, due date, or category.",
                    intent=command.intent,
                    entities=entities,
                    follow_up_required=True
                )

            # Call Phase 2 API to update the task
            task_result = phase2_client.update_task(str(user_id), auth_token, task_id, update_data)

            logger.log_task_operation(
                user_id=str(user_id),
                operation="UPDATE_TASK",
                success=True,
                details={"task_id": task_id, "updates": update_data}
            )

            return ProcessedCommandResult(
                success=True,
                message=f"I've updated the task: '{task_result.get('title', 'Unknown')}'",
                intent=command.intent,
                entities=entities,
                task_result=task_result,
                suggestions=[
                    "Show me this task",
                    "Show me all my tasks",
                    "Update another task"
                ]
            )

        except Exception as e:
            logger.error(f"Error updating task: {str(e)}", command=command.dict())
            return ProcessedCommandResult(
                success=False,
                message=f"Sorry, I couldn't update the task: {str(e)}",
                intent=command.intent,
                entities=entities,
                follow_up_required=True
            )

    def handle_completion(self, command: NaturalLanguageCommand, auth_token: str) -> ProcessedCommandResult:
        """
        Handle completion of a task
        """
        try:
            user_id = command.user_id
            entities = command.entities

            # Find the task to mark as complete
            task_id = entities.get('task_id')
            search_term = entities.get('search_term') or entities.get('task_title')

            if not search_term and not task_id:
                return ProcessedCommandResult(
                    success=False,
                    message="No task specified to complete. Please specify which task you want to mark as complete.",
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
                task_to_complete = tasks[0]
                task_id = task_to_complete.get('id')

            # Call Phase 2 API to update task completion status
            task_result = phase2_client.toggle_task_completion(str(user_id), auth_token, task_id, True)

            logger.log_task_operation(
                user_id=str(user_id),
                operation="COMPLETE_TASK",
                success=True,
                details={"task_id": task_id}
            )

            return ProcessedCommandResult(
                success=True,
                message=f"I've marked the task '{task_result.get('title', 'Unknown')}' as complete!",
                intent=command.intent,
                entities=entities,
                task_result=task_result,
                suggestions=[
                    "Show me my incomplete tasks",
                    "Show me all my tasks",
                    "Mark another task as complete"
                ]
            )

        except Exception as e:
            logger.error(f"Error completing task: {str(e)}", command=command.dict())
            return ProcessedCommandResult(
                success=False,
                message=f"Sorry, I couldn't complete the task: {str(e)}",
                intent=command.intent,
                entities=entities,
                follow_up_required=True
            )


# Global instance for reuse
update_task_handler = UpdateTaskHandler()