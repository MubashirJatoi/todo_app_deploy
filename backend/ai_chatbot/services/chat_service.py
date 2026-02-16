import re
from typing import Dict, List, Tuple, Optional
from ai_chatbot.models.chat_models import TaskOperationRequest, TaskOperationResponse
from routes.tasks import TaskCreate, TaskUpdate
from sqlmodel import Session
from uuid import UUID
import uuid
from ai_chatbot.services.task_operations import (
    get_user_tasks_service,
    create_task_service,
    update_task_service,
    delete_task_service,
    complete_task_service
)


class ChatbotService:
    """
    Service class to handle AI chatbot functionality for todo management.
    Parses natural language and translates to task operations.
    """

    def __init__(self):
        # Define patterns for different operations
        self.patterns = {
            'create': [
                r'add.*task.*to\s+(.+)',
                r'create.*task.*to\s+(.+)',
                r'new.*task.*to\s+(.+)',
                r'make.*task.*to\s+(.+)',
                r'add\s+(.+)',
                r'create\s+(.+)',
            ],
            'update': [
                r'(?:update|change|modify|edit)\s+(?:the\s+)?task\s+(.+?)\s+(?:title|name)\s+(?:to|as)\s+(.+)',
                r'(?:update|change|modify|edit)\s+(?:the\s+)?task\s+(.+?)\s+(?:description)\s+(?:to|as)\s+(.+)',
                r'(?:update|change|modify|edit)\s+(?:the\s+)?task\s+(.+?)\s+(?:priority)\s+(?:to|as)\s+(.+)',
                r'(?:update|change|modify|edit)\s+(?:the\s+)?task\s+(.+?)\s+(?:due date|date)\s+(?:to|as)\s+(.+)',
                r'(?:update|change|modify|edit)\s+(?:the\s+)?(.+?)\s+(?:title|name)\s+(?:to|as)\s+(.+)',
                r'(?:update|change|modify|edit)\s+(?:the\s+)?(.+?)\s+(?:description)\s+(?:to|as)\s+(.+)',
                r'(?:update|change|modify|edit)\s+(?:the\s+)?(.+?)\s+(?:priority)\s+(?:to|as)\s+(.+)',
                r'(?:update|change|modify|edit)\s+(?:the\s+)?(.+?)\s+(?:due date|date)\s+(?:to|as)\s+(.+)',
                r'(?:update|change|modify|edit)\s+(?:the\s+)?task\s+(.+)',
                r'(?:update|change|modify|edit)\s+(?:the\s+)?(.+)',
            ],
            'complete': [
                r'complete.*task.*(.+)',
                r'finish.*task.*(.+)',
                r'mark.*task.*as.*done',
                r'done.*with.*task.*(.+)',
                r'finished.*task.*(.+)',
            ],
            'delete': [
                r'delete.*task.*(.+)',
                r'remove.*task.*(.+)',
                r'drop.*task.*(.+)',
            ],
            'list': [
                r'show.*task',
                r'list.*task',
                r'view.*task',
                r'what.*task',
                r'all.*task',
            ],
            'search': [
                r'find.*task.*(.+)',
                r'search.*task.*(.+)',
                r'look.*for.*task.*(.+)',
            ]
        }

    def parse_intent(self, message: str) -> Tuple[str, Dict[str, str]]:
        """
        Parse the user's natural language message to determine intent and extract entities.
        """
        message_lower = message.lower().strip()

        # Check for different operation types
        for operation, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    # Extract the relevant text for the operation
                    if match.groups():
                        extracted_text = match.group(1).strip()
                    else:
                        extracted_text = message_lower

                    if operation == 'create':
                        # For create operations, treat the extracted text as the task title
                        return operation, {'title': extracted_text}
                    elif operation == 'update':
                        # For update operations, extract based on the matched pattern
                        if match.groups():
                            if len(match.groups()) == 2:
                                # Pattern captured both task identifier and new value
                                task_identifier = match.group(1).strip()
                                new_value = match.group(2).strip()

                                # Determine what attribute is being updated based on the original message
                                message_lower = message.lower()
                                if 'title' in message_lower or 'name' in message_lower:
                                    return operation, {'search_term': task_identifier, 'title': new_value}
                                elif 'description' in message_lower:
                                    return operation, {'search_term': task_identifier, 'description': new_value}
                                elif 'priority' in message_lower:
                                    return operation, {'search_term': task_identifier, 'priority': new_value}
                                elif 'due date' in message_lower or 'date' in message_lower:
                                    return operation, {'search_term': task_identifier, 'due_date': new_value}
                                else:
                                    # If not clear what to update, return both parts
                                    return operation, {'search_term': task_identifier, 'title': new_value}
                            elif len(match.groups()) == 1:
                                # Pattern captured only one element (likely the task identifier)
                                task_identifier = match.group(1).strip()
                                return operation, {'search_term': task_identifier}
                        else:
                            # If no groups, use the full match
                            return operation, {'search_term': extracted_text}
                    elif operation in ['complete', 'delete']:
                        # For complete/delete, we need to find the task by title
                        return operation, {'search_term': extracted_text}
                    elif operation == 'search':
                        return 'list', {'search_term': extracted_text}
                    elif operation == 'list':
                        return operation, {}

        # Default to list if no specific intent found
        return 'list', {}

    def create_task_request(self, title: str) -> TaskOperationRequest:
        """
        Create a task operation request for creating a task.
        """
        return TaskOperationRequest(
            operation='create',
            title=title
        )

    def search_tasks_request(self, search_term: str) -> TaskOperationRequest:
        """
        Create a task operation request for searching tasks.
        """
        return TaskOperationRequest(
            operation='search',
            title=search_term
        )

    def complete_task_request(self, search_term: str) -> TaskOperationRequest:
        """
        Create a task operation request for completing a task.
        """
        return TaskOperationRequest(
            operation='update',
            title=search_term,
            completed=True
        )

    def delete_task_request(self, search_term: str) -> TaskOperationRequest:
        """
        Create a task operation request for deleting a task.
        """
        return TaskOperationRequest(
            operation='delete',
            title=search_term
        )

    def update_task_request(self, search_term: str, **kwargs) -> TaskOperationRequest:
        """
        Create a task operation request for updating a task.
        """
        return TaskOperationRequest(
            operation='update',
            title=search_term,
            **kwargs
        )

    def process_message(self, message: str, session: Session, user_id: UUID) -> str:
        """
        Process a natural language message and return a response.
        This integrates with actual task services to perform operations.
        """
        intent, entities = self.parse_intent(message)

        if intent == 'create':
            title = entities.get('title', 'Untitled task')
            try:
                # Create the task using the service
                new_task = create_task_service(
                    session=session,
                    user_id=user_id,
                    title=title
                )
                return f"I've created the task: '{new_task.title}'"
            except Exception as e:
                return f"Sorry, I couldn't create the task: {str(e)}"

        elif intent == 'complete':
            search_term = entities.get('search_term', '')
            try:
                # Find tasks matching the search term
                tasks = get_user_tasks_service(session, user_id, search=search_term)
                if tasks:
                    # Complete the first matching task
                    task_to_complete = tasks[0]
                    updated_task = complete_task_service(
                        session=session,
                        task_id=task_to_complete.id,
                        user_id=user_id,
                        completed=True
                    )
                    return f"I've marked the task '{updated_task.title}' as complete."
                else:
                    return f"I couldn't find any tasks containing '{search_term}'."
            except Exception as e:
                return f"Sorry, I couldn't complete the task: {str(e)}"

        elif intent == 'update':
            search_term = entities.get('search_term', '')
            try:
                # Find tasks matching the search term
                tasks = get_user_tasks_service(session, user_id, search=search_term)
                if tasks:
                    # Update the first matching task
                    task_to_update = tasks[0]

                    # Prepare update data based on entities
                    title = entities.get('title')
                    description = entities.get('description')
                    priority = entities.get('priority')
                    due_date_str = entities.get('due_date')

                    # Call update service with the collected update data
                    updated_task = update_task_service(
                        session=session,
                        task_id=task_to_update.id,
                        user_id=user_id,
                        title=title,
                        description=description,
                        priority=priority,
                        due_date=due_date_str
                    )

                    if updated_task:
                        return f"I've updated the task '{updated_task.title}'."
                    else:
                        return f"I couldn't update the task '{task_to_update.title}'."
                else:
                    return f"I couldn't find any tasks containing '{search_term}'."
            except Exception as e:
                return f"Sorry, I couldn't update the task: {str(e)}"

        elif intent == 'delete':
            search_term = entities.get('search_term', '')
            try:
                # Find tasks matching the search term
                tasks = get_user_tasks_service(session, user_id, search=search_term)
                if tasks:
                    # Delete the first matching task
                    task_to_delete = tasks[0]
                    success = delete_task_service(
                        session=session,
                        task_id=task_to_delete.id,
                        user_id=user_id
                    )
                    if success:
                        return f"I've deleted the task '{task_to_delete.title}'."
                    else:
                        return f"I couldn't delete the task '{task_to_delete.title}'."
                else:
                    return f"I couldn't find any tasks containing '{search_term}'."
            except Exception as e:
                return f"Sorry, I couldn't delete the task: {str(e)}"

        elif intent == 'list':
            search_term = entities.get('search_term', '')
            try:
                # Get tasks with optional search
                if search_term:
                    tasks = get_user_tasks_service(session, user_id, search=search_term)
                    if tasks:
                        task_titles = [task.title for task in tasks]
                        return f"Here are your tasks containing '{search_term}': {', '.join(task_titles)}"
                    else:
                        return f"You don't have any tasks containing '{search_term}'."
                else:
                    tasks = get_user_tasks_service(session, user_id)
                    if tasks:
                        task_titles = [task.title for task in tasks[:5]]  # Limit to first 5
                        if len(tasks) > 5:
                            return f"Here are your first 5 tasks: {', '.join(task_titles)}. You have {len(tasks)} total tasks."
                        else:
                            return f"Here are your tasks: {', '.join(task_titles)}"
                    else:
                        return "You don't have any tasks yet."
            except Exception as e:
                return f"Sorry, I couldn't retrieve your tasks: {str(e)}"
        else:
            return "I can help you manage your tasks. Try saying something like 'Add a task to buy groceries' or 'Show me my tasks'."