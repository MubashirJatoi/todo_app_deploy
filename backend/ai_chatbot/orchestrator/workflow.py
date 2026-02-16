from typing import Dict, Any, Optional
from ai_chatbot.orchestrator.agent import chatbot_orchestration_agent
from ai_chatbot.services.conversation_state import conversation_state_manager
from ai_chatbot.utils.logging import logger
from ai_chatbot.models.responses import ChatResponse
import uuid


class ChatProcessingWorkflow:
    """
    Main workflow for processing chat interactions in the AI chatbot
    """

    def __init__(self):
        self.orchestration_agent = chatbot_orchestration_agent
        self.conversation_manager = conversation_state_manager

    def process_chat_message(self, user_message: str, user_id: str, auth_token: str, conversation_id: str = None) -> ChatResponse:
        """
        Main workflow method to process a chat message
        """
        try:
            # Step 1: Get or create conversation state
            if not conversation_id:
                conversation_id = self.conversation_manager.create_conversation(user_id)
            else:
                existing_conv = self.conversation_manager.get_conversation(conversation_id)
                if not existing_conv:
                    conversation_id = self.conversation_manager.create_conversation(user_id)

            # Add user message to conversation history
            self.conversation_manager.add_message(conversation_id, "user", user_message)

            # Step 2: Check for pending actions in the conversation state
            pending_action = self.conversation_manager.get_pending_action(conversation_id)

            # Step 3: Process the message through the orchestration agent
            if pending_action:
                # Handle conversation with context of pending action
                result = self.orchestration_agent.handle_conversation_step(
                    user_message, user_id, auth_token,
                    {"pending_action": pending_action}
                )
            else:
                # Process as a new message
                result = self.orchestration_agent.process_user_message(
                    user_message, user_id, auth_token
                )

            # Step 4: Determine response based on processing result
            response_text = result.get("response", "I'm not sure how to respond to that.")

            # Step 5: Handle follow-up requirements
            if result.get("requires_follow_up", False):
                # Set conversation state to indicate follow-up is needed
                self.conversation_manager.update_conversation_state(conversation_id, "AWAITING_CLARIFICATION")

                # Add bot message to conversation history
                self.conversation_manager.add_message(conversation_id, "assistant", response_text)

                chat_response = ChatResponse(
                    conversation_id=conversation_id,
                    response=response_text,
                    intent=result.get("intent", "unknown"),
                    entities=result.get("entities", {}),
                    suggestions=result.get("suggestions", []),
                    timestamp=str(self._get_current_timestamp())
                )
            else:
                # Update conversation state to active
                self.conversation_manager.update_conversation_state(conversation_id, "ACTIVE")

                # Add bot message to conversation history
                self.conversation_manager.add_message(conversation_id, "assistant", response_text)

                chat_response = ChatResponse(
                    conversation_id=conversation_id,
                    response=response_text,
                    intent=result.get("intent", "unknown"),
                    entities=result.get("entities", {}),
                    suggestions=result.get("suggestions", []),
                    timestamp=str(self._get_current_timestamp())
                )

            # Step 6: Log the interaction
            logger.log_interaction(
                user_id=user_id,
                conversation_id=conversation_id,
                input_text=user_message,
                output_text=response_text,
                intent=result.get("intent", "unknown")
            )

            return chat_response

        except Exception as e:
            logger.error(f"Error in chat processing workflow: {str(e)}",
                         user_id=user_id,
                         conversation_id=conversation_id,
                         message=user_message)

            # Return an error response
            return ChatResponse(
                conversation_id=conversation_id or str(uuid.uuid4()),
                response="Sorry, I encountered an error processing your message. Please try again.",
                intent="error",
                entities={},
                suggestions=[],
                timestamp=str(self._get_current_timestamp())
            )

    def process_clarification_response(self, user_response: str, user_id: str, auth_token: str, conversation_id: str) -> ChatResponse:
        """
        Process a response to a clarification request
        """
        try:
            # Get the conversation state to understand what was being clarified
            conversation = self.conversation_manager.get_conversation(conversation_id)
            if not conversation:
                return ChatResponse(
                    conversation_id=conversation_id,
                    response="I couldn't find your conversation. Let's start fresh.",
                    intent="restart",
                    entities={},
                    suggestions=[],
                    timestamp=str(self._get_current_timestamp())
                )

            # Process the clarification response
            result = self.orchestration_agent.handle_conversation_step(
                user_response, user_id, auth_token,
                {"conversation_state": conversation}
            )

            response_text = result.get("response", "Thanks for the clarification.")

            # Update conversation state
            self.conversation_manager.add_message(conversation_id, "user", user_response)
            self.conversation_manager.add_message(conversation_id, "assistant", response_text)
            self.conversation_manager.update_conversation_state(conversation_id, "ACTIVE")

            # Clear any pending actions if resolved
            if not result.get("requires_follow_up", False):
                self.conversation_manager.clear_pending_action(conversation_id)

            return ChatResponse(
                conversation_id=conversation_id,
                response=response_text,
                intent=result.get("intent", "clarification_processed"),
                entities=result.get("entities", {}),
                suggestions=result.get("suggestions", []),
                timestamp=str(self._get_current_timestamp())
            )

        except Exception as e:
            logger.error(f"Error processing clarification: {str(e)}",
                         user_id=user_id,
                         conversation_id=conversation_id,
                         response=user_response)

            return ChatResponse(
                conversation_id=conversation_id,
                response="Sorry, I had trouble processing your clarification. Could you rephrase?",
                intent="clarification_error",
                entities={},
                suggestions=[],
                timestamp=str(self._get_current_timestamp())
            )

    def start_confirmation_flow(self, action_data: Dict[str, Any], user_id: str, conversation_id: str) -> ChatResponse:
        """
        Start a confirmation flow for potentially destructive actions
        """
        try:
            # Set the conversation state to require confirmation
            confirmation_data = {
                "type": "confirmation_required",
                "action": action_data.get("action"),
                "details": action_data.get("details"),
                "timestamp": self._get_current_timestamp()
            }

            self.conversation_manager.set_pending_action(conversation_id, confirmation_data)
            self.conversation_manager.update_conversation_state(conversation_id, "CONFIRMATION_REQUIRED")

            # Prepare confirmation message
            action_type = action_data.get("action", "an action")
            details = action_data.get("details", {})

            confirmation_msg = f"Please confirm that you want to {action_type}"
            if "task_title" in details:
                confirmation_msg += f" for task '{details['task_title']}'"
            confirmation_msg += ". Respond with 'yes' to confirm or 'no' to cancel."

            # Add confirmation request to conversation history
            self.conversation_manager.add_message(conversation_id, "assistant", confirmation_msg)

            return ChatResponse(
                conversation_id=conversation_id,
                response=confirmation_msg,
                intent="confirmation_required",
                entities={},
                suggestions=["yes", "no"],
                timestamp=str(self._get_current_timestamp())
            )

        except Exception as e:
            logger.error(f"Error starting confirmation flow: {str(e)}",
                         user_id=user_id,
                         conversation_id=conversation_id,
                         action_data=action_data)

            return ChatResponse(
                conversation_id=conversation_id,
                response="Sorry, I couldn't set up the confirmation. Proceeding with the action.",
                intent="confirmation_error",
                entities={},
                suggestions=[],
                timestamp=str(self._get_current_timestamp())
            )

    def handle_confirmation_response(self, user_response: str, user_id: str, auth_token: str, conversation_id: str) -> ChatResponse:
        """
        Handle user response to a confirmation request
        """
        try:
            # Get the pending action
            pending_action = self.conversation_manager.get_pending_action(conversation_id)
            if not pending_action:
                return self.process_chat_message(
                    user_response, user_id, auth_token, conversation_id
                )

            # Determine if user confirmed or denied
            user_input_lower = user_response.lower().strip()
            confirmed = any(word in user_input_lower for word in ["yes", "y", "confirm", "ok", "sure", "affirmative", "proceed"])
            denied = any(word in user_input_lower for word in ["no", "n", "deny", "cancel", "stop", "reject"])

            if confirmed:
                # User confirmed, execute the original action
                original_action = pending_action.get("action")
                action_details = pending_action.get("details", {})

                # Execute the confirmed action (this would typically involve reconstructing the original command)
                # For now, we'll simulate a successful execution
                response_text = f"Confirmed. {original_action} has been executed."

                # Clear the pending action
                self.conversation_manager.clear_pending_action(conversation_id)
                self.conversation_manager.update_conversation_state(conversation_id, "ACTIVE")

                # Add to conversation history
                self.conversation_manager.add_message(conversation_id, "user", user_response)
                self.conversation_manager.add_message(conversation_id, "assistant", response_text)

                result = {
                    "response": response_text,
                    "success": True,
                    "intent": "action_confirmed",
                    "entities": {}
                }
            elif denied:
                # User denied, cancel the action
                response_text = "Action cancelled as requested."

                # Clear the pending action
                self.conversation_manager.clear_pending_action(conversation_id)
                self.conversation_manager.update_conversation_state(conversation_id, "ACTIVE")

                # Add to conversation history
                self.conversation_manager.add_message(conversation_id, "user", user_response)
                self.conversation_manager.add_message(conversation_id, "assistant", response_text)

                result = {
                    "response": response_text,
                    "success": True,
                    "intent": "action_cancelled",
                    "entities": {}
                }
            else:
                # Unclear response, ask for clarification
                response_text = "I didn't understand your response. Please respond with 'yes' to confirm or 'no' to cancel."

                # Keep the pending action active
                self.conversation_manager.add_message(conversation_id, "user", user_response)
                self.conversation_manager.add_message(conversation_id, "assistant", response_text)

                result = {
                    "response": response_text,
                    "success": False,
                    "requires_follow_up": True,
                    "intent": "awaiting_confirmation",
                    "entities": {}
                }

            return ChatResponse(
                conversation_id=conversation_id,
                response=result["response"],
                intent=result["intent"],
                entities=result.get("entities", {}),
                suggestions=result.get("suggestions", []),
                timestamp=str(self._get_current_timestamp())
            )

        except Exception as e:
            logger.error(f"Error handling confirmation response: {str(e)}",
                         user_id=user_id,
                         conversation_id=conversation_id,
                         response=user_response)

            return ChatResponse(
                conversation_id=conversation_id,
                response="Sorry, I had trouble processing your confirmation response.",
                intent="confirmation_error",
                entities={},
                suggestions=[],
                timestamp=str(self._get_current_timestamp())
            )

    def _get_current_timestamp(self):
        """
        Helper method to get current timestamp
        """
        from datetime import datetime
        return datetime.now()


# Global instance for reuse
chat_processing_workflow = ChatProcessingWorkflow()