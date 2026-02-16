from typing import Dict, Optional
from ai_chatbot.models.command import NaturalLanguageCommand, ProcessedCommandResult, IntentType
from ai_chatbot.services.phase2_client import phase2_client
from ai_chatbot.utils.logging import logger


class CreateTaskHandler:
    """
    Handler for creating new tasks based on natural language input
    """

    def handle(self, command: NaturalLanguageCommand, auth_token: str) -> ProcessedCommandResult:
        """
        Handle create task command
        """
        try:
            user_id = command.user_id
            entities = command.entities

            # Extract task details from entities
            title = entities.get('task_title', '').strip()
            if not title:
                # Try to extract from raw input if not found in entities
                title = self._extract_title_from_raw(command.raw_input)

            if not title:
                return ProcessedCommandResult(
                    success=False,
                    message="No task title provided. Please specify what task you want to create.",
                    intent=command.intent,
                    entities=entities,
                    follow_up_required=True
                )

            # Extract other optional task details
            description = entities.get('description', '')
            priority = entities.get('priority', 'medium')  # Default to medium
            due_date = entities.get('due_date')

            # Prepare task data for API call
            task_data = {
                "title": title,
                "description": description,
                "priority": priority
            }

            if due_date:
                task_data["due_date"] = due_date

            # Call Phase 2 API to create the task
            task_result = phase2_client.create_task(str(user_id), auth_token, task_data)

            logger.log_task_operation(
                user_id=str(user_id),
                operation="CREATE_TASK",
                success=True,
                details={"title": title, "task_id": task_result.get('id')}
            )

            return ProcessedCommandResult(
                success=True,
                message=f"I've created the task: '{title}'",
                intent=command.intent,
                entities=entities,
                task_result=task_result,
                suggestions=[
                    f"Mark '{title}' as complete when done",
                    "Show me all my tasks",
                    "Add another task"
                ]
            )

        except Exception as e:
            logger.error(f"Error creating task: {str(e)}", command=command.dict())
            return ProcessedCommandResult(
                success=False,
                message=f"Sorry, I couldn't create the task: {str(e)}",
                intent=command.intent,
                entities=entities,
                follow_up_required=True
            )

    def _extract_title_from_raw(self, raw_input: str) -> str:
        """
        Extract task title from raw input if not found in entities
        """
        # Remove common verbs and phrases to isolate the task title
        import re

        # Remove common task creation phrases
        patterns = [
            r'(?:add|create|make|new|set up|establish)\s+(?:a\s+)?(?:task\s+to\s+|to\s+|that\s+|for\s+)',
            r'(?:please\s+|can you\s+|could you\s+)?(?:add|create|make|new|set up|establish)',
        ]

        title = raw_input.lower().strip()
        for pattern in patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)

        # Clean up the result
        title = title.strip(' .!?')
        if title:
            # Capitalize first letter
            title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()

        return title


# Global instance for reuse
create_task_handler = CreateTaskHandler()