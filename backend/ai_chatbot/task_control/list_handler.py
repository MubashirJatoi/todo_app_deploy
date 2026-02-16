from typing import Dict, Optional
from ai_chatbot.models.command import NaturalLanguageCommand, ProcessedCommandResult, IntentType
from ai_chatbot.services.phase2_client import phase2_client
from ai_chatbot.utils.logging import logger


class ListTasksHandler:
    """
    Handler for listing tasks based on natural language input
    """

    def handle(self, command: NaturalLanguageCommand, auth_token: str) -> ProcessedCommandResult:
        """
        Handle list tasks command
        """
        try:
            user_id = command.user_id
            entities = command.entities

            # Prepare filters based on entities
            filters = {}

            # Check for status filters
            if 'status' in entities:
                filters['status'] = entities['status']
            elif 'completed' in entities:
                # If completed is mentioned, filter accordingly
                if entities['completed'].lower() in ['true', 'yes', 'done']:
                    filters['status'] = 'completed'
                else:
                    filters['status'] = 'pending'

            # Check for priority filters
            if 'priority' in entities:
                filters['priority'] = entities['priority']

            # Check for category filters
            if 'category' in entities:
                filters['category'] = entities['category']

            # Check for sorting preferences
            if 'sort' in entities:
                filters['sort'] = entities['sort']

            # Call Phase 2 API to get tasks
            tasks = phase2_client.get_user_tasks(str(user_id), auth_token, filters)

            if not tasks:
                if filters:
                    # If filters were applied and no tasks found, mention the filters
                    filter_desc = ", ".join([f"{k}: {v}" for k, v in filters.items()])
                    message = f"You don't have any tasks with the filters ({filter_desc})."
                else:
                    message = "You don't have any tasks yet."

                return ProcessedCommandResult(
                    success=True,
                    message=message,
                    intent=command.intent,
                    entities=entities,
                    suggestions=[
                        "Add a new task",
                        "Show all tasks without filters"
                    ]
                )

            # Format the response based on number of tasks
            task_count = len(tasks)
            if task_count == 1:
                task_summary = f"You have 1 task: '{tasks[0]['title']}'"
            elif task_count <= 5:
                task_titles = [task['title'] for task in tasks]
                task_summary = f"You have {task_count} tasks: {', '.join(task_titles)}"
            else:
                # For more than 5 tasks, just show count and first few
                first_five_titles = [task['title'] for task in tasks[:5]]
                task_summary = f"You have {task_count} tasks. Here are the first 5: {', '.join(first_five_titles)}"

            logger.log_task_operation(
                user_id=str(user_id),
                operation="LIST_TASKS",
                success=True,
                details={"task_count": task_count, "filters": filters}
            )

            return ProcessedCommandResult(
                success=True,
                message=task_summary,
                intent=command.intent,
                entities=entities,
                task_result={"tasks": tasks, "count": task_count},
                suggestions=[
                    "Show only completed tasks",
                    "Show high priority tasks",
                    "Add a new task"
                ]
            )

        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}", command=command.dict())
            return ProcessedCommandResult(
                success=False,
                message=f"Sorry, I couldn't retrieve your tasks: {str(e)}",
                intent=command.intent,
                entities=entities,
                follow_up_required=True
            )

    def handle_with_filters(self, command: NaturalLanguageCommand, auth_token: str, filters: Dict) -> ProcessedCommandResult:
        """
        Handle list tasks command with specific filters
        """
        try:
            user_id = command.user_id
            entities = command.entities

            # Call Phase 2 API to get filtered tasks
            tasks = phase2_client.get_user_tasks(str(user_id), auth_token, filters)

            if not tasks:
                filter_desc = ", ".join([f"{k}: {v}" for k, v in filters.items()])
                message = f"You don't have any tasks with the filters ({filter_desc})."

                return ProcessedCommandResult(
                    success=True,
                    message=message,
                    intent=command.intent,
                    entities=entities,
                    suggestions=[
                        "Show all tasks",
                        "Try different filters"
                    ]
                )

            # Format the response
            task_count = len(tasks)
            if task_count <= 5:
                task_titles = [task['title'] for task in tasks]
                task_summary = f"You have {task_count} filtered tasks: {', '.join(task_titles)}"
            else:
                first_five_titles = [task['title'] for task in tasks[:5]]
                task_summary = f"You have {task_count} filtered tasks. Here are the first 5: {', '.join(first_five_titles)}"

            return ProcessedCommandResult(
                success=True,
                message=task_summary,
                intent=command.intent,
                entities=entities,
                task_result={"tasks": tasks, "count": task_count, "filters_applied": filters}
            )

        except Exception as e:
            logger.error(f"Error listing tasks with filters: {str(e)}", command=command.dict())
            return ProcessedCommandResult(
                success=False,
                message=f"Sorry, I couldn't retrieve your filtered tasks: {str(e)}",
                intent=command.intent,
                entities=entities,
                follow_up_required=True
            )


# Global instance for reuse
list_tasks_handler = ListTasksHandler()