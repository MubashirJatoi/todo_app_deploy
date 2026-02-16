from typing import Dict, Any
from ai_chatbot.nlp_intent.agent import nlp_intent_agent
from ai_chatbot.task_control.agent import task_control_agent
from ai_chatbot.user_context.agent import user_context_agent
from ai_chatbot.backend_integration.agent import backend_integration_agent
from ai_chatbot.response_composer.agent import response_composer_agent
from ai_chatbot.quality_guard.agent import quality_guard_agent
from ai_chatbot.models.command import NaturalLanguageCommand
from ai_chatbot.utils.logging import logger


class ChatbotOrchestrationAgent:
    """
    Main orchestration agent that coordinates all components of the AI chatbot
    """

    def __init__(self):
        self.nlp_agent = nlp_intent_agent
        self.task_control = task_control_agent
        self.user_context = user_context_agent
        self.backend_integration = backend_integration_agent
        self.response_composer = response_composer_agent
        self.quality_guard = quality_guard_agent

    def process_user_message(self, message: str, user_id: str, auth_token: str) -> Dict[str, Any]:
        """
        Process a user message through the entire pipeline
        """
        try:
            # Step 1: Validate input quality and safety
            validation_result = self.quality_guard.validate_and_process(message, user_id)
            if not validation_result["proceed"]:
                return {
                    "response": validation_result["message"],
                    "success": False,
                    "requires_follow_up": False
                }

            # Step 2: Get user context
            user_info = self.user_context.get_user_info(auth_token)
            if not user_info.get("authenticated"):
                return {
                    "response": "You need to be authenticated to use this service.",
                    "success": False,
                    "requires_follow_up": False
                }

            # Step 3: Process natural language input
            command = self.nlp_agent.process_input(message, user_id)

            # Step 4: Validate the command
            command_validation = self.quality_guard.validate_command(command)
            if not command_validation["is_valid"]:
                return {
                    "response": command_validation["message"],
                    "success": False,
                    "requires_follow_up": command_validation.get("requires_confirmation", False)
                }

            # Step 5: Execute the task based on intent
            result = self.task_control.execute_command(command, auth_token)

            # Step 6: Validate the result for safety
            if result.task_result:
                safety_check = self.quality_guard.check_safety(str(result.task_result))
                if not safety_check["is_safe"]:
                    return {
                        "response": "The result of your request contains content that is not safe to display.",
                        "success": False,
                        "requires_follow_up": False
                    }

            # Step 7: Compose the response
            final_response = self.response_composer.compose_final_response(result, message)

            logger.log_interaction(
                user_id=user_id,
                conversation_id=command.conversation_id or "unknown",
                input_text=message,
                output_text=final_response.get("response", ""),
                intent=str(command.intent),
                entities=command.entities
            )

            return final_response

        except Exception as e:
            logger.error(f"Error in chatbot orchestration: {str(e)}",
                         user_id=user_id,
                         message=message)

            return {
                "response": "Sorry, I encountered an error while processing your request. Please try again.",
                "success": False,
                "requires_follow_up": False,
                "error": str(e)
            }

    def process_task_command(self, command: NaturalLanguageCommand, auth_token: str) -> Dict[str, Any]:
        """
        Process a specific task command through the orchestration pipeline
        """
        try:
            # Validate the command
            command_validation = self.quality_guard.validate_command(command)
            if not command_validation["is_valid"]:
                return {
                    "response": command_validation["message"],
                    "success": False,
                    "requires_follow_up": command_validation.get("requires_confirmation", False)
                }

            # Validate task operation in context
            task_validation = self.quality_guard.validate_task_operation(command)
            if not task_validation["is_valid"]:
                if task_validation.get("requires_confirmation"):
                    return {
                        "response": task_validation["message"],
                        "success": False,
                        "requires_follow_up": True
                    }
                else:
                    return {
                        "response": task_validation["message"],
                        "success": False,
                        "requires_follow_up": False
                    }

            # Execute the task
            result = self.task_control.execute_command(command, auth_token)

            # Compose response
            final_response = self.response_composer.compose_final_response(result, command.raw_input)

            logger.log_interaction(
                user_id=str(command.user_id) if command.user_id else "unknown",
                conversation_id=command.conversation_id or "unknown",
                input_text=command.raw_input,
                output_text=final_response.get("response", ""),
                intent=str(command.intent),
                entities=command.entities
            )

            return final_response

        except Exception as e:
            logger.error(f"Error processing task command: {str(e)}", command=command.dict())
            return {
                "response": "Sorry, I encountered an error while processing your task command.",
                "success": False,
                "requires_follow_up": False,
                "error": str(e)
            }

    def handle_conversation_step(self, message: str, user_id: str, auth_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle a single step in a conversation, considering context
        """
        try:
            # If there's ongoing context (like a pending action), handle that first
            if context and context.get("pending_action"):
                # Handle the pending action
                pending_action = context["pending_action"]
                return self._handle_pending_action(pending_action, message, user_id, auth_token)

            # Otherwise, process as a new message
            return self.process_user_message(message, user_id, auth_token)

        except Exception as e:
            logger.error(f"Error in conversation step: {str(e)}",
                         user_id=user_id,
                         message=message,
                         context=context)
            return {
                "response": "Sorry, I encountered an error in the conversation flow.",
                "success": False,
                "requires_follow_up": False,
                "error": str(e)
            }

    def _handle_pending_action(self, pending_action: Dict[str, Any], user_input: str, user_id: str, auth_token: str) -> Dict[str, Any]:
        """
        Handle a pending action based on user input
        """
        action_type = pending_action.get("type")
        action_data = pending_action.get("data", {})

        if action_type == "confirmation_required":
            # Check if user confirmed or denied
            user_input_lower = user_input.lower()
            if any(conf_word in user_input_lower for conf_word in ["yes", "y", "sure", "ok", "confirm", "affirmative"]):
                # User confirmed, proceed with the action
                command = action_data.get("command")
                if command:
                    # Reconstruct the command and execute it
                    cmd_obj = NaturalLanguageCommand(**command)
                    return self.process_task_command(cmd_obj, auth_token)
            elif any(deny_word in user_input_lower for deny_word in ["no", "n", "cancel", "stop", "deny"]):
                # User denied, cancel the action
                return {
                    "response": "Action cancelled.",
                    "success": True,
                    "requires_follow_up": False
                }
            else:
                # Unclear response, ask for clarification
                return {
                    "response": "Please confirm or deny the action.",
                    "success": False,
                    "requires_follow_up": True
                }

        # Default: treat as a new message
        return self.process_user_message(user_input, user_id, auth_token)


# Global instance for reuse
chatbot_orchestration_agent = ChatbotOrchestrationAgent()