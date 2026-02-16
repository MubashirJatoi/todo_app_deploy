from typing import Dict, Any, List
from ai_chatbot.models.command import ProcessedCommandResult, IntentType
import random


class ResponseFormatter:
    """
    Formatter for creating human-friendly responses based on command results
    """

    def __init__(self):
        # Positive responses for successful operations
        self.positive_responses = [
            "Great! ",
            "Sure thing! ",
            "Done! ",
            "Alright! ",
            "Perfect! "
        ]

        # Negative responses for failed operations
        self.negative_responses = [
            "I'm sorry, ",
            "Unfortunately, ",
            "Hmm, it seems ",
            "Looks like ",
            "Unfortunately, I couldn't "
        ]

    def format_response(self, result: ProcessedCommandResult, original_command: str = "") -> str:
        """
        Format a response based on the processed command result
        """
        if result.success:
            return self._format_success_response(result)
        else:
            return self._format_error_response(result.message, original_command)

    def format_error_response(self, error_message: str, original_command: str = "") -> str:
        """
        Format an error response
        """
        # Choose a random negative prefix
        prefix = random.choice(self.negative_responses)

        # If there's a specific error message, use it
        if error_message:
            return f"{prefix}{error_message}"
        else:
            return f"{prefix}I couldn't complete that request. Could you try rephrasing?"

    def format_suggestions(self, suggestions: List[str]) -> str:
        """
        Format suggestions for the user
        """
        if not suggestions:
            return ""

        # Random greeting for suggestions
        greetings = [
            "Here are some things you might want to try: ",
            "You could also: ",
            "Consider doing: ",
            "You might want to: "
        ]

        greeting = random.choice(greetings)
        suggestions_text = ", or ".join(suggestions)

        return f"{greeting}{suggestions_text}."

    def format_follow_up(self, result: ProcessedCommandResult) -> str:
        """
        Format a follow-up request when additional input is needed
        """
        intent = result.intent

        if intent == IntentType.CREATE_TASK:
            return "What would you like to name your task?"
        elif intent == IntentType.UPDATE_TASK:
            return "Which task would you like to update, and what changes would you like to make?"
        elif intent == IntentType.DELETE_TASK:
            return "Which task would you like to delete?"
        elif intent == IntentType.COMPLETE_TASK:
            return "Which task would you like to mark as complete?"
        elif intent == IntentType.SEARCH_TASKS:
            return "What are you looking for in your tasks?"
        else:
            return "Could you please provide more details?"

    def _format_success_response(self, result: ProcessedCommandResult) -> str:
        """
        Format a success response based on the intent
        """
        intent = result.intent
        message = result.message

        if intent == IntentType.CREATE_TASK:
            if message:
                return f"{random.choice(self.positive_responses)}{message}"
            else:
                return f"{random.choice(self.positive_responses)}I've created a new task for you."

        elif intent == IntentType.UPDATE_TASK:
            if message:
                return f"{random.choice(self.positive_responses)}{message}"
            else:
                return f"{random.choice(self.positive_responses)}I've updated your task."

        elif intent == IntentType.COMPLETE_TASK:
            if message:
                return f"{random.choice(self.positive_responses)}{message}"
            else:
                return f"{random.choice(self.positive_responses)}I've marked the task as complete."

        elif intent == IntentType.DELETE_TASK:
            if message:
                return f"{random.choice(self.positive_responses)}{message}"
            else:
                return f"{random.choice(self.positive_responses)}I've deleted the task."

        elif intent == IntentType.LIST_TASKS:
            if result.task_result and len(result.task_result) > 0:
                count = len(result.task_result)
                return f"You have {count} task{'s' if count != 1 else ''}. {message or ''}".strip()
            else:
                return "You don't have any tasks at the moment."

        elif intent == IntentType.SEARCH_TASKS:
            if result.task_result and len(result.task_result) > 0:
                count = len(result.task_result)
                return f"I found {count} matching task{'s' if count != 1 else ''}. {message or ''}".strip()
            else:
                return "I couldn't find any tasks matching your search."

        elif intent == IntentType.FILTER_TASKS:
            if result.task_result and 'count' in result.task_result:
                count = result.task_result['count']
                return f"I found {count} filtered task{'s' if count != 1 else ''}. {message or ''}".strip()
            elif result.task_result and len(result.task_result) > 0:
                count = len(result.task_result)
                return f"I found {count} filtered task{'s' if count != 1 else ''}. {message or ''}".strip()
            else:
                return "I couldn't find any tasks matching your filters."

        elif intent == IntentType.GET_USER_INFO:
            return message or "Here's the information you requested."

        else:
            # Generic positive response
            if message:
                return f"{random.choice(self.positive_responses)}{message}"
            else:
                return f"{random.choice(self.positive_responses)}I've completed your request."

    def format_task_list_response(self, tasks: List[Dict[str, Any]]) -> str:
        """
        Format a response for a list of tasks
        """
        if not tasks:
            return "You don't have any tasks at the moment."

        task_titles = [task.get('title', 'Untitled Task') for task in tasks]
        task_list = ", ".join(task_titles[:5])  # Limit to first 5 tasks

        if len(tasks) > 5:
            remaining = len(tasks) - 5
            return f"Here are your tasks: {task_list}, and {remaining} more."
        else:
            return f"Here are your tasks: {task_list}."


# Global instance for reuse
response_formatter = ResponseFormatter()