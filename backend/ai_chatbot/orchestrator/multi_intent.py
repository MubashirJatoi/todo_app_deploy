"""
Module for handling multi-intent processing in the AI chatbot
"""
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from ai_chatbot.models.command import NaturalLanguageCommand, IntentType, ProcessedCommandResult
from ai_chatbot.nlp_intent.agent import nlp_intent_agent
from ai_chatbot.task_control.agent import task_control_agent
from ai_chatbot.response_composer.agent import response_composer_agent
from ai_chatbot.quality_guard.agent import quality_guard_agent
from ai_chatbot.utils.logging import logger


class MultiIntentStrategy(Enum):
    """Strategies for handling multiple intents in a single user input"""
    SEQUENTIAL = "SEQUENTIAL"           # Process intents one by one in sequence
    PARALLEL = "PARALLEL"              # Process intents simultaneously (where possible)
    HIERARCHICAL = "HIERARCHICAL"       # Process intents based on priority/order of importance
    COMPOSITE = "COMPOSITE"            # Combine multiple intents into a single composite action


@dataclass
class MultiIntentResult:
    """Result of multi-intent processing"""
    success: bool
    results: List[ProcessedCommandResult]
    message: str
    suggestions: List[str]
    follow_up_required: bool = False


class MultiIntentProcessor:
    """Processes user inputs that contain multiple intents"""

    def __init__(self):
        self.intent_separator_patterns = [
            r'\band\b',           # "and"
            r';',                 # semicolon
            r'\.',                # period
            r'\?|\!',             # question mark or exclamation
            r',\s*and\s*',        # comma followed by "and"
            r'(?<!\w)\&(?!&)',    # standalone ampersand
        ]

        # Define intent priorities for hierarchical processing
        self.intent_priority_map = {
            IntentType.UNKNOWN: 0,
            IntentType.LIST_TASKS: 1,
            IntentType.SEARCH_TASKS: 2,
            IntentType.FILTER_TASKS: 3,
            IntentType.SORT_TASKS: 4,
            IntentType.CREATE_TASK: 5,
            IntentType.UPDATE_TASK: 6,
            IntentType.DELETE_TASK: 7,
            IntentType.GET_USER_INFO: 8,
            IntentType.CANCELLED: 9,
        }

    def extract_multiple_intents(self, raw_input: str) -> List[str]:
        """
        Extract multiple intent statements from a single raw input

        Args:
            raw_input: The raw user input that may contain multiple intents

        Returns:
            List of individual intent statements
        """
        import re

        # Normalize the input
        normalized_input = raw_input.strip()

        # Split the input based on separator patterns
        parts = [normalized_input]

        for pattern in self.intent_separator_patterns:
            new_parts = []
            for part in parts:
                # Split but keep the separators to understand context
                split_parts = re.split(f'({pattern})', part)

                # Reconstruct with separators treated as intent boundaries
                reconstructed = []
                current_part = ""

                for item in split_parts:
                    if re.match(pattern, item.strip(), re.IGNORECASE):
                        if current_part.strip():
                            reconstructed.append(current_part.strip())
                            current_part = ""
                    else:
                        current_part += item

                if current_part.strip():
                    reconstructed.append(current_part.strip())

                new_parts.extend([p for p in reconstructed if p.strip()])

            parts = new_parts

        # Clean up and filter out empty parts
        cleaned_parts = [part.strip() for part in parts if part.strip()]

        # Further refine by looking for common phrases that indicate separate intents
        refined_parts = []
        for part in cleaned_parts:
            # Check for compound commands like "add task X and complete task Y"
            if ' and ' in part.lower():
                sub_parts = part.split(' and ')
                refined_parts.extend([sub_part.strip() for sub_part in sub_parts if sub_part.strip()])
            else:
                refined_parts.append(part)

        return refined_parts

    def process_multi_intent_command(self,
                                   raw_input: str,
                                   user_id: str,
                                   auth_token: str,
                                   strategy: MultiIntentStrategy = MultiIntentStrategy.SEQUENTIAL) -> MultiIntentResult:
        """
        Process a command that contains multiple intents

        Args:
            raw_input: The raw user input that may contain multiple intents
            user_id: The ID of the user making the request
            auth_token: The authentication token for the user
            strategy: The strategy to use for processing multiple intents

        Returns:
            MultiIntentResult containing the results of processing all intents
        """
        try:
            # Extract individual intent statements
            intent_statements = self.extract_multiple_intents(raw_input)

            if len(intent_statements) <= 1:
                # If there's only one statement, treat as single intent
                return self._process_single_intent(raw_input, user_id, auth_token)

            logger.info(f"Processing {len(intent_statements)} intents from single input",
                       user_id=user_id, intent_count=len(intent_statements))

            # Process each intent statement
            results = []
            all_successful = True
            combined_suggestions = []

            if strategy == MultiIntentStrategy.SEQUENTIAL:
                results = self._process_sequentially(intent_statements, user_id, auth_token)
            elif strategy == MultiIntentStrategy.HIERARCHICAL:
                results = self._process_hierarchically(intent_statements, user_id, auth_token)
            else:
                # Default to sequential processing
                results = self._process_sequentially(intent_statements, user_id, auth_token)

            # Aggregate results
            for result in results:
                if not result.success:
                    all_successful = False
                if result.suggestions:
                    combined_suggestions.extend(result.suggestions)

            # Create a summary message
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)

            if all_successful:
                message = f"Successfully processed {success_count} of {total_count} requests."
            else:
                message = f"Processed {success_count} of {total_count} requests. Some operations had issues."

            return MultiIntentResult(
                success=all_successful,
                results=results,
                message=message,
                suggestions=combined_suggestions[:5],  # Limit suggestions
                follow_up_required=not all_successful
            )

        except Exception as e:
            logger.error(f"Error in multi-intent processing: {str(e)}",
                        user_id=user_id, raw_input=raw_input)
            return MultiIntentResult(
                success=False,
                results=[],
                message="Error processing multiple intents in your request",
                suggestions=["Try separating your requests", "Ask one thing at a time"]
            )

    def _process_single_intent(self, raw_input: str, user_id: str, auth_token: str) -> MultiIntentResult:
        """Process a single intent as a multi-intent result"""
        # Use the existing NLP intent agent to classify the intent
        classified_command = nlp_intent_agent.classify_intent(raw_input)
        classified_command.user_id = user_id

        # Validate the command with quality guard
        validation_result = quality_guard_agent.validate_command(classified_command)
        if not validation_result["is_valid"]:
            return MultiIntentResult(
                success=False,
                results=[],
                message=validation_result["message"],
                suggestions=["Rephrase your request", "Be more specific"]
            )

        # Process with task control agent
        processed_result = task_control_agent.process_command(classified_command, auth_token)

        return MultiIntentResult(
            success=processed_result.success,
            results=[processed_result],
            message=processed_result.message,
            suggestions=processed_result.suggestions or [],
            follow_up_required=processed_result.follow_up_required
        )

    def _process_sequentially(self, intent_statements: List[str], user_id: str, auth_token: str) -> List[ProcessedCommandResult]:
        """Process intents sequentially, one after another"""
        results = []

        for statement in intent_statements:
            try:
                # Process each statement individually
                classified_command = nlp_intent_agent.classify_intent(statement)
                classified_command.user_id = user_id

                # Validate the command
                validation_result = quality_guard_agent.validate_command(classified_command)
                if not validation_result["is_valid"]:
                    results.append(ProcessedCommandResult(
                        success=False,
                        message=validation_result["message"],
                        intent=classified_command.intent,
                        entities=classified_command.entities,
                        suggestions=validation_result.get("suggestions", [])
                    ))
                    continue

                # Process with task control agent
                processed_result = task_control_agent.process_command(classified_command, auth_token)
                results.append(processed_result)

            except Exception as e:
                logger.error(f"Error processing intent statement: {str(e)}",
                           user_id=user_id, statement=statement)
                results.append(ProcessedCommandResult(
                    success=False,
                    message=f"Error processing: {statement}",
                    intent=None,
                    entities={},
                    suggestions=["Rephrase this part of your request"]
                ))

        return results

    def _process_hierarchically(self, intent_statements: List[str], user_id: str, auth_token: str) -> List[ProcessedCommandResult]:
        """Process intents hierarchically based on priority"""
        # Classify all intents first
        classified_commands = []
        for statement in intent_statements:
            command = nlp_intent_agent.classify_intent(statement)
            command.user_id = user_id
            classified_commands.append(command)

        # Sort by priority (higher priority first)
        classified_commands.sort(key=lambda cmd: self.intent_priority_map.get(cmd.intent, 0), reverse=True)

        results = []
        for command in classified_commands:
            try:
                # Validate the command
                validation_result = quality_guard_agent.validate_command(command)
                if not validation_result["is_valid"]:
                    results.append(ProcessedCommandResult(
                        success=False,
                        message=validation_result["message"],
                        intent=command.intent,
                        entities=command.entities,
                        suggestions=validation_result.get("suggestions", [])
                    ))
                    continue

                # Process with task control agent
                processed_result = task_control_agent.process_command(command, auth_token)
                results.append(processed_result)

            except Exception as e:
                logger.error(f"Error processing prioritized intent: {str(e)}",
                           user_id=user_id, intent=command.intent)
                results.append(ProcessedCommandResult(
                    success=False,
                    message=f"Error processing: {command.raw_input}",
                    intent=command.intent,
                    entities=command.entities,
                    suggestions=["Try this request separately"]
                ))

        return results

    def detect_multi_intent(self, raw_input: str) -> bool:
        """
        Detect if the input contains multiple intents

        Args:
            raw_input: The raw user input to analyze

        Returns:
            True if multiple intents are detected, False otherwise
        """
        intent_statements = self.extract_multiple_intents(raw_input)
        return len(intent_statements) > 1


# Global instance for reuse
multi_intent_processor = MultiIntentProcessor()