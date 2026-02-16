from typing import Dict, Optional
from ai_chatbot.models.command import NaturalLanguageCommand, ProcessedCommandResult, IntentType
from ai_chatbot.services.phase2_client import phase2_client
from ai_chatbot.utils.logging import logger


class SortTasksHandler:
    """
    Handler for sorting tasks based on natural language input
    """

    def handle(self, command: NaturalLanguageCommand, auth_token: str) -> ProcessedCommandResult:
        """
        Handle sort tasks command
        """
        try:
            user_id = command.user_id
            entities = command.entities

            # Determine sort criteria from entities or raw input
            sort_by = entities.get('sort_by') or entities.get('sort') or 'created_at'

            # Validate and normalize sort field
            valid_sort_fields = {
                'title': 'title',
                'priority': 'priority',
                'status': 'status',
                'due_date': 'due_date',
                'created_at': 'created_at',
                'updated_at': 'updated_at',
                'name': 'title',
                'date': 'due_date',
                'priority_level': 'priority'
            }

            # Check if the provided sort field is valid
            normalized_sort_field = None
            for key, value in valid_sort_fields.items():
                if key.lower() in sort_by.lower() or value.lower() in sort_by.lower():
                    normalized_sort_field = value
                    break

            if not normalized_sort_field:
                # Default to created_at if no valid sort field found
                normalized_sort_field = 'created_at'

            # Determine sort order
            sort_order = entities.get('sort_order', 'asc')
            if 'desc' in sort_order.lower() or 'reverse' in sort_order.lower() or 'high' in sort_order.lower():
                sort_order = 'desc'
            elif 'asc' in sort_order.lower() or 'low' in sort_order.lower():
                sort_order = 'asc'
            else:
                # Default to descending for priority and due_date, ascending for others
                if normalized_sort_field in ['priority', 'due_date']:
                    sort_order = 'desc'
                else:
                    sort_order = 'asc'

            # Prepare filters with sort parameters
            filters = {
                'sort': f"{normalized_sort_field}:{sort_order}"
            }

            # Add any additional filters from entities
            if 'status' in entities:
                filters['status'] = entities['status']
            if 'priority' in entities:
                filters['priority'] = entities['priority']
            if 'category' in entities:
                filters['category'] = entities['category']
            if 'search' in entities or 'search_term' in entities:
                filters['search'] = entities.get('search') or entities.get('search_term')

            # Call Phase 2 API to get sorted tasks
            tasks = phase2_client.get_user_tasks(str(user_id), auth_token, filters)

            if not tasks:
                message = f"You don't have any tasks to sort."

                return ProcessedCommandResult(
                    success=True,
                    message=message,
                    intent=command.intent,
                    entities=entities,
                    suggestions=[
                        "Show all my tasks",
                        "Add a new task",
                        "Try a different sort order"
                    ]
                )

            # Format the response based on number of tasks
            task_count = len(tasks)
            sort_description = self._get_sort_description(normalized_sort_field, sort_order)

            if task_count == 1:
                task_summary = f"I found 1 task, sorted by {sort_description}: '{tasks[0]['title']}'"
            elif task_count <= 5:
                task_titles = [task['title'] for task in tasks]
                task_summary = f"I found {task_count} tasks, sorted by {sort_description}: {', '.join(task_titles)}"
            else:
                # For more than 5 tasks, just show count and first few
                first_five_titles = [task['title'] for task in tasks[:5]]
                task_summary = f"I found {task_count} tasks, sorted by {sort_description}. Here are the first 5: {', '.join(first_five_titles)}"

            logger.log_task_operation(
                user_id=str(user_id),
                operation="SORT_TASKS",
                success=True,
                details={"task_count": task_count, "sort_by": normalized_sort_field, "sort_order": sort_order, "filters": filters}
            )

            return ProcessedCommandResult(
                success=True,
                message=task_summary,
                intent=command.intent,
                entities=entities,
                task_result={"tasks": tasks, "count": task_count, "sorted_by": normalized_sort_field, "order": sort_order},
                suggestions=[
                    "Show tasks sorted differently",
                    "Show all tasks without sorting",
                    "Add a new task"
                ]
            )

        except Exception as e:
            logger.error(f"Error sorting tasks: {str(e)}", command=command.dict())
            return ProcessedCommandResult(
                success=False,
                message=f"Sorry, I couldn't sort your tasks: {str(e)}",
                intent=command.intent,
                entities=entities,
                follow_up_required=True
            )

    def _get_sort_description(self, sort_field: str, sort_order: str) -> str:
        """
        Get a human-readable description of the sort criteria
        """
        field_names = {
            'title': 'title',
            'priority': 'priority',
            'status': 'status',
            'due_date': 'due date',
            'created_at': 'creation date',
            'updated_at': 'update date'
        }

        field_name = field_names.get(sort_field, sort_field)
        order_name = "descending" if sort_order == "desc" else "ascending"

        return f"{field_name} ({order_name})"


# Global instance for reuse
sort_tasks_handler = SortTasksHandler()