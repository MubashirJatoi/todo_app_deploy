"""
Service for generating clarification requests when user input is ambiguous
"""
from typing import Dict, List, Optional, Any
from enum import Enum
from ..models.command import NaturalLanguageCommand, IntentType


class ClarificationType(Enum):
    """Types of clarifications that may be needed"""
    AMBIGUOUS_TASK_REFERENCE = "AMBIGUOUS_TASK_REFERENCE"
    UNCLEAR_INTENT = "UNCLEAR_INTENT"
    MISSING_ENTITY = "MISSING_ENTITY"
    MULTIPLE_POSSIBLE_ACTIONS = "MULTIPLE_POSSIBLE_ACTIONS"


class ClarificationRequest:
    """Represents a clarification request to be sent to the user"""

    def __init__(self, clarification_type: ClarificationType, message: str,
                 suggestions: Optional[List[str]] = None, context: Optional[Dict[str, Any]] = None):
        self.type = clarification_type
        self.message = message
        self.suggestions = suggestions or []
        self.context = context or {}


class ClarificationGenerator:
    """Generates appropriate clarification requests for ambiguous user inputs"""

    def __init__(self):
        self.clarification_templates = {
            ClarificationType.AMBIGUOUS_TASK_REFERENCE: [
                "Which task do you mean? I found multiple tasks that match your description.",
                "Could you clarify which specific task you're referring to?",
                "There are multiple tasks that could match your request. Could you be more specific?"
            ],
            ClarificationType.UNCLEAR_INTENT: [
                "I'm not sure what you'd like me to do. Could you clarify your request?",
                "Could you provide more details about what you'd like to accomplish?",
                "I need more information to understand your request. What would you like me to do?"
            ],
            ClarificationType.MISSING_ENTITY: [
                "I need more information to complete this request. What is the title or description of the task?",
                "Could you provide the task title or details for what you'd like to do?",
                "I need more specifics to create or update the task. What should it be called?"
            ],
            ClarificationType.MULTIPLE_POSSIBLE_ACTIONS: [
                "I can help you with multiple actions. Which one would you like to do?",
                "There are several things I can do based on your request. Which action did you want?",
                "I can perform multiple operations. Please specify which one you'd like."
            ]
        }

    def generate_clarification_request(self, command: NaturalLanguageCommand,
                                    clarification_type: ClarificationType,
                                    candidates: Optional[List[Dict[str, Any]]] = None) -> ClarificationRequest:
        """
        Generate a clarification request based on the command and clarification type

        Args:
            command: The original command that needs clarification
            clarification_type: The type of clarification needed
            candidates: Optional list of candidate tasks or options that need clarification

        Returns:
            ClarificationRequest object with appropriate message
        """
        template_messages = self.clarification_templates.get(clarification_type, ["I need clarification on your request."])

        # Select an appropriate message based on the clarification type and context
        message = template_messages[0]  # Default to first template

        # Customize message based on specific context
        if clarification_type == ClarificationType.AMBIGUOUS_TASK_REFERENCE and candidates:
            if len(candidates) > 1:
                task_titles = [candidate.get('title', 'unnamed task') for candidate in candidates[:3]]
                task_list_str = ", ".join(task_titles)
                message = f"I found multiple tasks that match your request: {task_list_str}. Could you specify which one you mean?"

        elif clarification_type == ClarificationType.MISSING_ENTITY:
            if command.intent == IntentType.CREATE_TASK:
                message = "I need a title for the task you want to create. What should I call it?"
            elif command.intent in [IntentType.UPDATE_TASK, IntentType.DELETE_TASK]:
                message = "I need to know which task you want to modify. Could you specify the task title?"

        elif clarification_type == ClarificationType.UNCLEAR_INTENT:
            message = f"I'm not sure what you meant by '{command.raw_input}'. Could you rephrase your request or be more specific?"

        # Generate helpful suggestions based on context
        suggestions = self._generate_suggestions(command, clarification_type, candidates)

        return ClarificationRequest(
            clarification_type=clarification_type,
            message=message,
            suggestions=suggestions
        )

    def _generate_suggestions(self, command: NaturalLanguageCommand,
                            clarification_type: ClarificationType,
                            candidates: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """Generate helpful suggestions based on the command and clarification type"""
        suggestions = []

        if clarification_type == ClarificationType.AMBIGUOUS_TASK_REFERENCE and candidates:
            # Provide specific task suggestions
            for i, candidate in enumerate(candidates[:3]):  # Limit to first 3 candidates
                title = candidate.get('title', 'unnamed task')
                suggestions.append(f"Choose '{title}'")

        elif clarification_type == ClarificationType.MISSING_ENTITY:
            if command.intent == IntentType.CREATE_TASK:
                suggestions.extend([
                    "Add task: [task title]",
                    "Create a task to [describe task]",
                    "Make a new task called [title]"
                ])

        elif clarification_type == ClarificationType.UNCLEAR_INTENT:
            # Provide general suggestions based on common commands
            suggestions.extend([
                "Add a task: [title]",
                "Complete task: [title]",
                "Delete task: [title]",
                "Show my tasks",
                "What can I do?"
            ])

        return suggestions

    def needs_clarification(self, command: NaturalLanguageCommand,
                          possible_matches: Optional[List[Dict[str, Any]]] = None) -> Optional[ClarificationRequest]:
        """
        Determine if a command needs clarification and return an appropriate clarification request

        Args:
            command: The command to evaluate
            possible_matches: Optional list of possible matches that are ambiguous

        Returns:
            ClarificationRequest if clarification is needed, None otherwise
        """
        # Check if the command has ambiguous references
        if possible_matches and len(possible_matches) > 1:
            return self.generate_clarification_request(
                command,
                ClarificationType.AMBIGUOUS_TASK_REFERENCE,
                possible_matches
            )

        # Check if intent is unclear
        if command.intent == IntentType.UNKNOWN:
            return self.generate_clarification_request(
                command,
                ClarificationType.UNCLEAR_INTENT
            )

        # Check if required entities are missing
        if command.intent in [IntentType.CREATE_TASK, IntentType.UPDATE_TASK] and not command.entities.get('title'):
            return self.generate_clarification_request(
                command,
                ClarificationType.MISSING_ENTITY
            )

        # Check for multiple possible interpretations
        if hasattr(command, '_multiple_intents') and getattr(command, '_multiple_intents', False):
            return self.generate_clarification_request(
                command,
                ClarificationType.MULTIPLE_POSSIBLE_ACTIONS
            )

        return None


# Global instance for reuse
clarification_generator = ClarificationGenerator()