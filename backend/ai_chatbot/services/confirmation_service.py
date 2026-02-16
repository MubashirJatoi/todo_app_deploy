"""
Service for handling confirmation requests for destructive actions
"""
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime, timedelta
import uuid
from ..models.command import NaturalLanguageCommand, ProcessedCommandResult


class ConfirmationType(Enum):
    """Types of confirmations that may be required"""
    DESTRUCTIVE_ACTION = "DESTRUCTIVE_ACTION"  # Delete tasks, clear all, etc.
    ACCOUNT_ACTION = "ACCOUNT_ACTION"          # Account changes
    DATA_MODIFICATION = "DATA_MODIFICATION"    # Bulk updates, etc.


class ConfirmationRequest:
    """Represents a confirmation request to be sent to the user"""

    def __init__(self, confirmation_type: ConfirmationType, message: str,
                 original_command: NaturalLanguageCommand,
                 action_to_confirm: str,
                 expires_in_minutes: int = 5):
        self.confirmation_id = str(uuid.uuid4())
        self.type = confirmation_type
        self.message = message
        self.original_command = original_command
        self.action_to_confirm = action_to_confirm
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(minutes=expires_in_minutes)
        self.is_confirmed = False
        self.is_rejected = False


class ConfirmationService:
    """Handles confirmation requests for destructive or important actions"""

    def __init__(self):
        # In-memory storage for confirmation requests
        # In production, this would use Redis or database
        self.pending_confirmations: Dict[str, ConfirmationRequest] = {}

    def create_confirmation_request(self, command: NaturalLanguageCommand,
                                 action_to_confirm: str,
                                 confirmation_type: ConfirmationType = ConfirmationType.DESTRUCTIVE_ACTION,
                                 custom_message: Optional[str] = None) -> ConfirmationRequest:
        """
        Create a confirmation request for a potentially destructive action

        Args:
            command: The original command that requires confirmation
            action_to_confirm: Description of the action that needs confirmation
            confirmation_type: Type of confirmation required
            custom_message: Optional custom message for the confirmation

        Returns:
            ConfirmationRequest object
        """
        if custom_message is None:
            if confirmation_type == ConfirmationType.DESTRUCTIVE_ACTION:
                custom_message = f"Are you sure you want to {action_to_confirm}? This action cannot be undone."
            elif confirmation_type == ConfirmationType.ACCOUNT_ACTION:
                custom_message = f"You are about to {action_to_confirm}. Confirm this action?"
            else:
                custom_message = f"Confirm: {action_to_confirm}"

        confirmation_request = ConfirmationRequest(
            confirmation_type=confirmation_type,
            message=custom_message,
            original_command=command,
            action_to_confirm=action_to_confirm
        )

        # Store the confirmation request
        self.pending_confirmations[confirmation_request.confirmation_id] = confirmation_request

        return confirmation_request

    def confirm_action(self, confirmation_id: str) -> bool:
        """
        Confirm an action by confirmation ID

        Args:
            confirmation_id: ID of the confirmation to accept

        Returns:
            True if confirmation was successful, False otherwise
        """
        if confirmation_id in self.pending_confirmations:
            confirmation = self.pending_confirmations[confirmation_id]
            if not self.is_expired(confirmation):
                confirmation.is_confirmed = True
                confirmation.is_rejected = False
                return True
        return False

    def reject_action(self, confirmation_id: str) -> bool:
        """
        Reject an action by confirmation ID

        Args:
            confirmation_id: ID of the confirmation to reject

        Returns:
            True if rejection was successful, False otherwise
        """
        if confirmation_id in self.pending_confirmations:
            confirmation = self.pending_confirmations[confirmation_id]
            if not self.is_expired(confirmation):
                confirmation.is_confirmed = False
                confirmation.is_rejected = True
                # Clean up the confirmation request
                del self.pending_confirmations[confirmation_id]
                return True
        return False

    def is_expired(self, confirmation: ConfirmationRequest) -> bool:
        """
        Check if a confirmation request has expired

        Args:
            confirmation: The confirmation request to check

        Returns:
            True if expired, False otherwise
        """
        return datetime.now() > confirmation.expires_at

    def get_confirmation_status(self, confirmation_id: str) -> Optional[ConfirmationRequest]:
        """
        Get the status of a confirmation request

        Args:
            confirmation_id: ID of the confirmation to check

        Returns:
            ConfirmationRequest if found, None if not found or expired
        """
        if confirmation_id in self.pending_confirmations:
            confirmation = self.pending_confirmations[confirmation_id]
            if self.is_expired(confirmation):
                # Clean up expired confirmation
                del self.pending_confirmations[confirmation_id]
                return None
            return confirmation
        return None

    def needs_confirmation(self, command: NaturalLanguageCommand,
                        action_description: str = "") -> Optional[ConfirmationRequest]:
        """
        Determine if a command needs confirmation and create a confirmation request if needed

        Args:
            command: The command to evaluate
            action_description: Optional description of the action (auto-generated if empty)

        Returns:
            ConfirmationRequest if confirmation is needed, None otherwise
        """
        # Define destructive actions that require confirmation
        destructive_patterns = [
            'delete all',
            'remove all',
            'clear all',
            'erase all',
            'destroy',
            'nuke',
            'wipe',
            'delete task'
        ]

        # Check if command contains destructive keywords
        command_lower = command.raw_input.lower()

        # Look for destructive patterns in the command
        is_destructive = any(pattern in command_lower for pattern in destructive_patterns)

        # Also check if it's a delete intent
        if hasattr(command, 'intent') and command.intent.name == 'DELETE_TASK':
            is_destructive = True

        if is_destructive:
            if not action_description:
                action_description = f"'{command.raw_input}'"

            return self.create_confirmation_request(
                command=command,
                action_to_confirm=action_description,
                confirmation_type=ConfirmationType.DESTRUCTIVE_ACTION
            )

        return None

    def process_confirmed_action(self, confirmation_id: str) -> Optional[ProcessedCommandResult]:
        """
        Process an action that has been confirmed

        Args:
            confirmation_id: ID of the confirmed action

        Returns:
            ProcessedCommandResult if successful, None if confirmation not found/expired
        """
        confirmation = self.get_confirmation_status(confirmation_id)

        if confirmation and confirmation.is_confirmed:
            # Execute the original command since it's been confirmed
            # For now, return a placeholder result - in practice, this would re-execute the original command
            result = ProcessedCommandResult(
                success=True,
                message=f"Confirmed and executed: {confirmation.action_to_confirm}",
                intent=confirmation.original_command.intent,
                entities=confirmation.original_command.entities,
                suggestions=["What else can I help you with?"]
            )

            # Clean up the confirmation
            del self.pending_confirmations[confirmation_id]

            return result

        return None

    def cleanup_expired_confirmations(self) -> int:
        """
        Remove expired confirmation requests and return count of removed confirmations

        Returns:
            Number of expired confirmations removed
        """
        current_time = datetime.now()
        expired_ids = []

        for conf_id, confirmation in self.pending_confirmations.items():
            if current_time > confirmation.expires_at:
                expired_ids.append(conf_id)

        for conf_id in expired_ids:
            del self.pending_confirmations[conf_id]

        return len(expired_ids)


# Global instance for reuse
confirmation_service = ConfirmationService()