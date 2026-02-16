from typing import Dict, Optional
from ai_chatbot.models.command import NaturalLanguageCommand, ProcessedCommandResult, IntentType
from ai_chatbot.services.phase2_client import phase2_client
from ai_chatbot.utils.logging import logger


class SearchTasksHandler:
    """
    Handler for searching tasks based on natural language input
    """

    def handle(self, command: NaturalLanguageCommand, auth_token: str) -> ProcessedCommandResult:
        """
        Handle search tasks command
        """
        try:
            user_id = command.user_id
            entities = command.entities

            # Get search term from entities or raw input
            search_term = entities.get('search_term') or entities.get('task_title')

            if not search_term:
                # Try to extract search term from raw input
                search_term = self._extract_search_term(command.raw_input)

            if not search_term:
                return ProcessedCommandResult(
                    success=False,
                    message="What would you like to search for in your tasks?",
                    intent=command.intent,
                    entities=entities,
                    follow_up_required=True
                )

            # Prepare filters with the search term
            filters = {"search": search_term}

            # Add any additional filters from entities
            if 'status' in entities:
                filters['status'] = entities['status']
            if 'priority' in entities:
                filters['priority'] = entities['priority']
            if 'category' in entities:
                filters['category'] = entities['category']
            if 'sort' in entities:
                filters['sort'] = entities['sort']

            # Call Phase 2 API to search tasks
            tasks = phase2_client.get_user_tasks(str(user_id), auth_token, filters)

            if not tasks:
                message = f"I couldn't find any tasks containing '{search_term}'."

                return ProcessedCommandResult(
                    success=True,
                    message=message,
                    intent=command.intent,
                    entities=entities,
                    suggestions=[
                        "Try a different search term",
                        "Show me all my tasks",
                        "Add a new task"
                    ]
                )

            # Format the response based on number of tasks found
            task_count = len(tasks)
            if task_count == 1:
                task_summary = f"I found 1 task containing '{search_term}': '{tasks[0]['title']}'"
            elif task_count <= 5:
                task_titles = [task['title'] for task in tasks]
                task_summary = f"I found {task_count} tasks containing '{search_term}': {', '.join(task_titles)}"
            else:
                # For more than 5 tasks, just show count and first few
                first_five_titles = [task['title'] for task in tasks[:5]]
                task_summary = f"I found {task_count} tasks containing '{search_term}'. Here are the first 5: {', '.join(first_five_titles)}"

            logger.log_task_operation(
                user_id=str(user_id),
                operation="SEARCH_TASKS",
                success=True,
                details={"search_term": search_term, "task_count": task_count, "filters": filters}
            )

            return ProcessedCommandResult(
                success=True,
                message=task_summary,
                intent=command.intent,
                entities=entities,
                task_result={"tasks": tasks, "count": task_count, "search_term": search_term},
                suggestions=[
                    f"Show tasks containing '{search_term}' with specific filters",
                    "Show me all my tasks",
                    "Add another task"
                ]
            )

        except Exception as e:
            logger.error(f"Error searching tasks: {str(e)}", command=command.dict())
            return ProcessedCommandResult(
                success=False,
                message=f"Sorry, I couldn't search for tasks: {str(e)}",
                intent=command.intent,
                entities=entities,
                follow_up_required=True
            )

    def _extract_search_term(self, raw_input: str) -> str:
        """
        Extract search term from raw input if not found in entities
        """
        import re

        # Look for patterns indicating a search
        patterns = [
            r'search.*for\s+(.+?)(?:\.|$)',
            r'find.*tasks?.*with\s+(.+?)(?:\.|$)',
            r'find.*tasks?.*containing\s+(.+?)(?:\.|$)',
            r'look.*for\s+(.+?)(?:\.|$)',
            r'show.*tasks?.*with\s+(.+?)(?:\.|$)',
            r'show.*tasks?.*containing\s+(.+?)(?:\.|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, raw_input, re.IGNORECASE)
            if match:
                term = match.group(1).strip()
                # Remove common articles and prepositions
                term = re.sub(r'\b(a|an|the|in|on|at|by|for|of|with|to|from|up|about|into|through|during|before|after|above|below|between|among)\b', '', term, flags=re.IGNORECASE)
                term = term.strip()
                return term

        # If no specific pattern found, return the raw input without command verbs
        # Remove common search verbs
        search_terms = raw_input.lower()
        for verb in ['search', 'find', 'look', 'show', 'for', 'tasks', 'task', 'please', 'can', 'you']:
            search_terms = re.sub(r'\b' + verb + r'\b', '', search_terms, flags=re.IGNORECASE)

        search_terms = search_terms.strip(' .!?')
        return search_terms if search_terms else ""


# Global instance for reuse
search_tasks_handler = SearchTasksHandler()