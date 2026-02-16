from typing import Dict, Any, Optional
from ai_chatbot.quality_guard.validator import quality_validator
from ai_chatbot.utils.logging import logger
from ai_chatbot.models.command import NaturalLanguageCommand


class QualityGuardAgent:
    """
    Agent responsible for ensuring quality, safety, and proper validation of user inputs and system responses
    """

    def __init__(self):
        self.validator = quality_validator

    def validate_input(self, user_input: str, user_id: str = None) -> Dict[str, Any]:
        """
        Validate user input for safety and appropriateness
        """
        try:
            validation_result = self.validator.validate_user_input(user_input)

            logger.info(
                f"Input validation completed",
                user_id=user_id,
                input_length=len(user_input),
                validation_passed=validation_result["is_valid"]
            )

            return validation_result
        except Exception as e:
            logger.error(f"Error validating input: {str(e)}",
                         user_id=user_id,
                         input=user_input)
            return {
                "is_valid": False,
                "reason": "Validation error",
                "message": "There was an error processing your input"
            }

    def validate_command(self, command: NaturalLanguageCommand) -> Dict[str, Any]:
        """
        Validate a natural language command for safety and completeness
        """
        try:
            validation_result = self.validator.validate_command(command)

            logger.info(
                f"Command validation completed",
                user_id=str(command.user_id) if command.user_id else None,
                intent=command.intent,
                validation_passed=validation_result["is_valid"]
            )

            return validation_result
        except Exception as e:
            logger.error(f"Error validating command: {str(e)}", command=command.dict())
            return {
                "is_valid": False,
                "reason": "Validation error",
                "message": "There was an error validating your command"
            }

    def validate_response(self, response: str, original_request: str = "") -> Dict[str, Any]:
        """
        Validate system response for appropriateness and safety
        """
        try:
            validation_result = self.validator.validate_response(response)

            logger.info(
                f"Response validation completed",
                original_request_length=len(original_request) if original_request else 0,
                response_length=len(response),
                validation_passed=validation_result["is_valid"]
            )

            return validation_result
        except Exception as e:
            logger.error(f"Error validating response: {str(e)}", response=response)
            return {
                "is_valid": False,
                "reason": "Validation error",
                "message": "There was an error validating the response"
            }

    def check_safety(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check if the text is safe according to safety guidelines
        """
        try:
            safety_result = self.validator.check_safety(text, context)

            logger.info(
                f"Safety check completed",
                text_length=len(text),
                is_safe=safety_result["is_safe"]
            )

            return safety_result
        except Exception as e:
            logger.error(f"Error in safety check: {str(e)}", text=text)
            return {
                "is_safe": False,
                "reason": "Safety check error",
                "message": "There was an error checking the safety of this content"
            }

    def validate_task_operation(self, command: NaturalLanguageCommand, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate that a task operation is appropriate given the user context
        """
        try:
            validation_result = self.validator.validate_task_operation(command, user_context)

            logger.info(
                f"Task operation validation completed",
                user_id=str(command.user_id) if command.user_id else None,
                intent=command.intent,
                validation_passed=validation_result["is_valid"]
            )

            return validation_result
        except Exception as e:
            logger.error(f"Error validating task operation: {str(e)}", command=command.dict())
            return {
                "is_valid": False,
                "reason": "Validation error",
                "message": "There was an error validating this task operation"
            }

    def validate_destructive_action_confirmation(self, confirmation_id: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate that a destructive action confirmation is appropriate and safe

        Args:
            confirmation_id: The ID of the confirmation being validated
            user_context: Context about the user making the request

        Returns:
            Dictionary with validation results
        """
        try:
            validation_result = self.validator.validate_destructive_action_confirmation(confirmation_id, user_context)

            logger.info(
                f"Destructive action confirmation validation completed",
                confirmation_id=confirmation_id,
                validation_passed=validation_result["is_valid"]
            )

            return validation_result
        except Exception as e:
            logger.error(f"Error validating destructive action confirmation: {str(e)}",
                        confirmation_id=confirmation_id)
            return {
                "is_valid": False,
                "reason": "Validation error",
                "message": "There was an error validating this confirmation"
            }

    def screen_for_policy_violations(self, text: str, user_id: str = None) -> Dict[str, Any]:
        """
        Screen text for potential policy violations
        """
        try:
            screening_result = self.validator.screen_content(text)

            logger.info(
                f"Policy screening completed",
                user_id=user_id,
                text_length=len(text),
                violations_found=len(screening_result.get("violations", []))
            )

            return screening_result
        except Exception as e:
            logger.error(f"Error in policy screening: {str(e)}", text=text)
            return {
                "has_violations": True,
                "violations": ["Screening error"],
                "message": "There was an error screening this content"
            }

    def validate_and_process(self, user_input: str, user_id: str = None) -> Dict[str, Any]:
        """
        Complete validation process for user input
        """
        try:
            # Step 1: Validate input safety
            input_validation = self.validate_input(user_input, user_id)
            if not input_validation["is_valid"]:
                return {
                    "proceed": False,
                    "reason": input_validation["reason"],
                    "message": input_validation["message"]
                }

            # Step 2: Check for policy violations
            policy_check = self.screen_for_policy_violations(user_input, user_id)
            if policy_check["has_violations"]:
                return {
                    "proceed": False,
                    "reason": "policy_violation",
                    "violations": policy_check["violations"],
                    "message": "Your input contains content that violates our policies"
                }

            # Step 3: If all validations pass
            return {
                "proceed": True,
                "message": "Input passed all validations"
            }

        except Exception as e:
            logger.error(f"Error in complete validation process: {str(e)}",
                         user_id=user_id,
                         input=user_input)
            return {
                "proceed": False,
                "reason": "validation_error",
                "message": "There was an error validating your input"
            }


# Global instance for reuse
quality_guard_agent = QualityGuardAgent()