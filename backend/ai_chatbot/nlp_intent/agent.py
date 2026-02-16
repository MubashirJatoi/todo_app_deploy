from typing import Dict, Tuple
from ai_chatbot.models.command import NaturalLanguageCommand, IntentType
from ai_chatbot.nlp_intent.classifier import intent_classifier
from ai_chatbot.nlp_intent.entity_extractor import entity_extractor
from ai_chatbot.utils.logging import logger


class NLPIntentAgent:
    """
    Agent responsible for processing natural language input and determining intent and entities
    """

    def __init__(self):
        self.intent_classifier = intent_classifier
        self.entity_extractor = entity_extractor

    def process_input(self, raw_input: str, user_id: str = None, conversation_id: str = None) -> NaturalLanguageCommand:
        """
        Process raw input and return a NaturalLanguageCommand object
        """
        try:
            # Classify intent
            intent, confidence = self.intent_classifier.classify_intent(raw_input)

            # Extract entities
            entities = self.entity_extractor.extract_entities(raw_input)

            # Create and return NaturalLanguageCommand object
            command = NaturalLanguageCommand(
                raw_input=raw_input,
                intent=intent,
                entities=entities,
                confidence=confidence,
                user_id=user_id,
                conversation_id=conversation_id
            )

            logger.info(
                f"Processed NLP input: intent={intent}, confidence={confidence}",
                raw_input=raw_input,
                intent=intent,
                entities=entities
            )

            return command

        except Exception as e:
            logger.error(f"Error processing NLP input: {str(e)}", raw_input=raw_input)
            # Return a command with unknown intent in case of error
            return NaturalLanguageCommand(
                raw_input=raw_input,
                intent=IntentType.UNKNOWN,
                entities={},
                confidence=0.0,
                user_id=user_id,
                conversation_id=conversation_id
            )

    def get_suggested_intents(self, text: str) -> Dict[IntentType, float]:
        """
        Get all possible intents with their confidence scores for the given text
        """
        try:
            # This would normally use a more sophisticated multi-classification approach
            primary_intent, confidence = self.intent_classifier.classify_intent(text)
            return {primary_intent: confidence}
        except Exception as e:
            logger.error(f"Error getting suggested intents: {str(e)}", text=text)
            return {IntentType.UNKNOWN: 0.0}

    def validate_command(self, command: NaturalLanguageCommand) -> bool:
        """
        Validate if the command has sufficient information to be processed
        """
        try:
            # Basic validation rules
            if command.intent == IntentType.UNKNOWN:
                return False

            # Some intents require specific entities
            if command.intent in [IntentType.CREATE_TASK] and 'task_title' not in command.entities:
                # For create task, we might be able to infer from raw input
                # So we'll allow it but with a lower confidence
                pass

            if command.intent in [IntentType.DELETE_TASK, IntentType.COMPLETE_TASK] and \
               'task_title' not in command.entities and 'search_term' not in command.entities:
                return False

            return True
        except Exception as e:
            logger.error(f"Error validating command: {str(e)}", command=command.dict())
            return False


# Global instance for reuse
nlp_intent_agent = NLPIntentAgent()