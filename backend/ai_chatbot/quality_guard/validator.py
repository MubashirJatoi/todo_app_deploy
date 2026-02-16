from typing import Dict, Any, List
from ai_chatbot.models.command import NaturalLanguageCommand
import re


class QualityValidator:
    """
    Validator for ensuring quality, safety, and appropriate content
    """

    def __init__(self):
        # Define potentially problematic patterns
        self.prohibited_patterns = [
            r'(\b(delete|drop|truncate|alter|drop table|insert into|select \* from)\b)',  # SQL keywords
            r'(\b(exec|system|os\.|subprocess\.)\b)',  # System execution
            r'(password|secret|key|token)\s*[:=]\s*\S+',  # Credential patterns
        ]

        # Define restricted topics
        self.restricted_topics = [
            'harassment',
            'threat',
            'violence',
            'hate speech',
            'explicit content',
            'spam',
            'scam'
        ]

    def validate_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Validate user input for safety and appropriateness
        """
        input_lower = user_input.lower()

        # Check for prohibited patterns
        for pattern in self.prohibited_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return {
                    "is_valid": False,
                    "reason": "contains_prohibited_content",
                    "message": "Your input contains potentially harmful content"
                }

        # Check for restricted topics
        for topic in self.restricted_topics:
            if topic in input_lower:
                return {
                    "is_valid": False,
                    "reason": "contains_restricted_topic",
                    "message": f"Your input contains content related to '{topic}' which is restricted"
                }

        # Basic length check
        if len(user_input.strip()) < 2:
            return {
                "is_valid": False,
                "reason": "too_short",
                "message": "Your input is too short to process"
            }

        # Check for excessive repetition
        if len(set(user_input.split())) / len(user_input.split()) < 0.2:  # Too repetitive
            return {
                "is_valid": False,
                "reason": "excessive_repetition",
                "message": "Your input contains too much repetition"
            }

        return {
            "is_valid": True,
            "reason": "valid",
            "message": "Input is valid"
        }

    def validate_command(self, command: NaturalLanguageCommand) -> Dict[str, Any]:
        """
        Validate a natural language command for safety and completeness
        """
        # Check if command has required attributes
        if not command.raw_input:
            return {
                "is_valid": False,
                "reason": "missing_raw_input",
                "message": "Command is missing raw input"
            }

        if not command.intent:
            return {
                "is_valid": False,
                "reason": "missing_intent",
                "message": "Command is missing intent"
            }

        # Validate entities if present
        if command.entities:
            for key, value in command.entities.items():
                if isinstance(value, str):
                    entity_validation = self.validate_user_input(value)
                    if not entity_validation["is_valid"]:
                        return {
                            "is_valid": False,
                            "reason": f"invalid_entity_{key}",
                            "message": f"Entity '{key}' contains invalid content"
                        }

        return {
            "is_valid": True,
            "reason": "valid_command",
            "message": "Command is valid"
        }

    def validate_response(self, response: str) -> Dict[str, Any]:
        """
        Validate system response for appropriateness and safety
        """
        response_lower = response.lower()

        # Check for problematic patterns in response
        for pattern in self.prohibited_patterns:
            if re.search(pattern, response_lower, re.IGNORECASE):
                return {
                    "is_valid": False,
                    "reason": "response_contains_prohibited_content",
                    "message": "Response contains potentially harmful content"
                }

        # Check for restricted topics
        for topic in self.restricted_topics:
            if topic in response_lower:
                return {
                    "is_valid": False,
                    "reason": "response_contains_restricted_topic",
                    "message": f"Response contains content related to '{topic}' which is restricted"
                }

        # Basic length check
        if len(response.strip()) < 1:
            return {
                "is_valid": False,
                "reason": "response_empty",
                "message": "Response is empty"
            }

        return {
            "is_valid": True,
            "reason": "valid_response",
            "message": "Response is valid"
        }

    def check_safety(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check if the text is safe according to safety guidelines
        """
        text_lower = text.lower()

        # Check for unsafe content
        safety_issues = []

        # Self-harm indicators
        self_harm_indicators = [
            'suicide', 'kill myself', 'end my life', 'self harm', 'hurt myself'
        ]
        for indicator in self_harm_indicators:
            if indicator in text_lower:
                safety_issues.append("potential_self_harm")

        # Violent threats
        threat_indicators = [
            'kill', 'murder', 'hurt', 'attack', 'destroy', 'harm'
        ]
        for indicator in threat_indicators:
            if indicator in text_lower and ('want to' in text_lower or 'will' in text_lower or 'going to' in text_lower):
                safety_issues.append("potential_violent_threat")

        # Explicit content
        explicit_indicators = [
            'porn', 'nude', 'sexually', 'explicit'
        ]
        for indicator in explicit_indicators:
            if indicator in text_lower:
                safety_issues.append("explicit_content")

        if safety_issues:
            return {
                "is_safe": False,
                "issues": safety_issues,
                "message": "Content contains safety issues"
            }

        return {
            "is_safe": True,
            "issues": [],
            "message": "Content is safe"
        }

    def validate_task_operation(self, command: NaturalLanguageCommand, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate that a task operation is appropriate given the user context
        """
        # Check for destructive operations that might need confirmation
        destructive_operations = ["DELETE_TASK", "UPDATE_TASK", "CLEAR_ALL_TASKS"]

        if command.intent.value in destructive_operations:
            entities = command.entities

            # Check if user is requesting deletion of all tasks or many tasks
            if command.intent.value == "DELETE_TASK":
                # Check for broad deletion terms
                search_term = entities.get('search_term', '').lower()
                title = entities.get('task_title', '').lower()

                # Check for terms indicating bulk deletion
                bulk_deletion_terms = ['all', 'everything', 'all tasks', 'every task', '*', 'bulk']

                if search_term in bulk_deletion_terms or title in bulk_deletion_terms:
                    return {
                        "is_valid": False,
                        "requires_confirmation": True,
                        "message": "Deleting all tasks requires confirmation",
                        "confirmation_reason": "bulk_deletion"
                    }

                # Check if raw input suggests destructive intent
                raw_input_lower = command.raw_input.lower()
                if any(term in raw_input_lower for term in ['delete everything', 'remove all', 'clear all']):
                    return {
                        "is_valid": False,
                        "requires_confirmation": True,
                        "message": "This bulk deletion operation requires confirmation",
                        "confirmation_reason": "bulk_deletion"
                    }

            # Check for other destructive operations that might need confirmation
            if command.intent.value == "UPDATE_TASK":
                # Check for operations that might affect multiple tasks
                if entities.get('search_term') or entities.get('filter'):
                    raw_input_lower = command.raw_input.lower()
                    # Check if the update is for multiple tasks
                    if any(term in raw_input_lower for term in ['all', 'every', 'each']):
                        return {
                            "is_valid": False,
                            "requires_confirmation": True,
                            "message": "Bulk update operation requires confirmation",
                            "confirmation_reason": "bulk_update"
                        }

        # Validate entities for the specific operation
        if command.intent.value in ["CREATE_TASK"] and not entities.get('task_title'):
            # For create tasks, we might be able to extract from raw input
            if not command.raw_input or len(command.raw_input.strip()) < 3:
                return {
                    "is_valid": False,
                    "reason": "insufficient_task_info",
                    "message": "Not enough information to create a task"
                }

        return {
            "is_valid": True,
            "requires_confirmation": False,
            "message": "Task operation is valid"
        }

    def validate_destructive_action_confirmation(self, confirmation_id: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate that a destructive action confirmation is appropriate

        Args:
            confirmation_id: The ID of the confirmation being validated
            user_context: Context about the user making the request

        Returns:
            Dictionary with validation results
        """
        # In a real implementation, this would check against stored confirmation requests
        # For now, we'll simulate the validation process

        # Check if user has appropriate permissions for destructive actions
        if user_context and user_context.get('permissions'):
            permissions = user_context['permissions']
            if 'execute_destructive_actions' not in permissions:
                return {
                    "is_valid": False,
                    "reason": "insufficient_permissions",
                    "message": "You don't have permission to perform this destructive action"
                }

        # Check rate limiting for destructive actions
        if user_context and user_context.get('destructive_action_count', 0) > 10:
            # If user has performed many destructive actions recently, require additional verification
            return {
                "is_valid": True,  # Still valid but with warning
                "requires_additional_verification": True,
                "message": "You've performed many destructive actions recently. Please proceed with caution."
            }

        # Check if the action being confirmed is indeed destructive
        # This would typically involve looking up the stored confirmation request
        # For simulation purposes, we'll return a positive validation
        return {
            "is_valid": True,
            "requires_additional_verification": False,
            "message": "Destructive action confirmation is valid"
        }

    def screen_content(self, text: str) -> Dict[str, Any]:
        """
        Screen text for potential policy violations
        """
        violations = []

        text_lower = text.lower()

        # Check for various violation types
        if len(re.findall(r'[!]{3,}', text)) > 3:  # Excessive punctuation
            violations.append("excessive_punctuation")

        if len(re.findall(r'CAPS LOCK', text)) > 0 or (len(text) > 10 and text.isupper()):
            violations.append("excessive_capitalization")

        # Check for prohibited patterns
        for pattern in self.prohibited_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                violations.append("prohibited_content")

        # Check for restricted topics
        for topic in self.restricted_topics:
            if topic in text_lower:
                violations.append("restricted_topic")

        return {
            "has_violations": len(violations) > 0,
            "violations": violations,
            "message": f"Content {'has' if violations else 'has no'} policy violations"
        }


# Global instance for reuse
quality_validator = QualityValidator()