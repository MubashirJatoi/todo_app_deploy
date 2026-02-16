from typing import Dict, Any, List
from ai_chatbot.models.command import ProcessedCommandResult
from ai_chatbot.response_composer.formatter import response_formatter
from ai_chatbot.utils.logging import logger


class ResponseComposerAgent:
    """
    Agent responsible for composing human-friendly responses based on processed commands
    """

    def __init__(self):
        self.formatter = response_formatter

    def compose_response(self, result: ProcessedCommandResult, original_command: str = "") -> str:
        """
        Compose a human-friendly response based on the processed command result
        """
        try:
            # Use the formatter to create a proper response
            response = self.formatter.format_response(result, original_command)

            logger.info(
                f"Composed response for intent: {result.intent}",
                intent=result.intent,
                success=result.success
            )

            return response
        except Exception as e:
            logger.error(f"Error composing response: {str(e)}", result=result.dict())
            return self._fallback_response(result)

    def compose_error_response(self, error_message: str, original_command: str = "") -> str:
        """
        Compose a human-friendly error response
        """
        try:
            response = self.formatter.format_error_response(error_message, original_command)

            logger.warning(
                f"Composed error response",
                error_message=error_message
            )

            return response
        except Exception as e:
            logger.error(f"Error composing error response: {str(e)}", error_message=error_message)
            return f"Sorry, I encountered an error: {error_message}"

    def compose_suggestions(self, suggestions: List[str]) -> str:
        """
        Compose a response with suggestions for the user
        """
        try:
            if not suggestions:
                return ""

            response = self.formatter.format_suggestions(suggestions)

            logger.info(
                f"Composed {len(suggestions)} suggestions",
                suggestion_count=len(suggestions)
            )

            return response
        except Exception as e:
            logger.error(f"Error composing suggestions: {str(e)}", suggestions=suggestions)
            return ""

    def compose_follow_up(self, result: ProcessedCommandResult) -> str:
        """
        Compose a follow-up response when additional input is needed
        """
        try:
            response = self.formatter.format_follow_up(result)

            logger.info(
                f"Composed follow-up response",
                requires_follow_up=result.follow_up_required
            )

            return response
        except Exception as e:
            logger.error(f"Error composing follow-up: {str(e)}", result=result.dict())
            return "I need more information to complete this task."

    def _fallback_response(self, result: ProcessedCommandResult) -> str:
        """
        Fallback response when formatting fails
        """
        if result.success:
            return result.message or f"Operation completed with result: {result.task_result}"
        else:
            return result.message or "Sorry, I couldn't complete the requested operation."

    def compose_final_response(self, result: ProcessedCommandResult, original_command: str = "") -> Dict[str, Any]:
        """
        Compose the final response with all necessary components
        """
        try:
            # Main response
            main_response = self.compose_response(result, original_command)

            # Suggestions if available
            suggestions = ""
            if result.suggestions:
                suggestions = self.compose_suggestions(result.suggestions)

            # Follow-up if needed
            follow_up = ""
            if result.follow_up_required:
                follow_up = self.compose_follow_up(result)

            final_response = {
                "response": main_response,
                "success": result.success,
                "intent": result.intent,
                "entities": result.entities,
                "follow_up_required": result.follow_up_required
            }

            if suggestions:
                final_response["suggestions"] = suggestions

            if follow_up:
                final_response["follow_up"] = follow_up

            # Log the final response composition
            logger.info(
                f"Final response composed",
                intent=result.intent,
                success=result.success,
                has_suggestions=bool(result.suggestions),
                has_follow_up=result.follow_up_required
            )

            return final_response

        except Exception as e:
            logger.error(f"Error composing final response: {str(e)}", result=result.dict())

            # Return a basic response in case of error
            return {
                "response": f"An error occurred while processing your request: {str(e)}",
                "success": False,
                "intent": str(result.intent),
                "follow_up_required": False
            }


# Global instance for reuse
response_composer_agent = ResponseComposerAgent()