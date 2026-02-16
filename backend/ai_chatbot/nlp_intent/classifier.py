from typing import Dict, List, Tuple
from ai_chatbot.models.command import IntentType
from ai_chatbot.services.cohere_client import CohereClient
from ai_chatbot.utils.logging import logger


class IntentClassifier:
    """
    Classifies user input into specific intents for the AI chatbot
    """

    def __init__(self):
        self.cohere_client = CohereClient()
        self.possible_intents = [intent.value for intent in IntentType if intent != IntentType.UNKNOWN]

    def classify_intent(self, text: str) -> Tuple[IntentType, float]:
        """
        Classify the intent of the given text
        Returns tuple of (intent, confidence_score)
        """
        try:
            # First try Cohere classification if API key is available
            if self.cohere_client.client:
                classified_intent = self.cohere_client.classify_intent(text, self.possible_intents)

                # Map the result to our IntentType
                for intent_type in IntentType:
                    if intent_type.value == classified_intent:
                        return intent_type, 0.8  # Assume high confidence from Cohere

                # If not matched, fall back to rule-based classification
                return self._rule_based_classify(text)
            else:
                # Fall back to rule-based classification
                return self._rule_based_classify(text)
        except Exception as e:
            logger.error(f"Error in intent classification: {str(e)}", text=text)
            # Fallback to rule-based if Cohere fails
            return self._rule_based_classify(text)

    def _rule_based_classify(self, text: str) -> Tuple[IntentType, float]:
        """
        Rule-based intent classification as fallback
        """
        text_lower = text.lower().strip()

        # Define patterns for each intent
        intent_patterns = {
            IntentType.CREATE_TASK: [
                'add.*task', 'create.*task', 'new.*task', 'make.*task', 'add', 'create'
            ],
            IntentType.UPDATE_TASK: [
                'update.*task', 'modify.*task', 'change.*task', 'update', 'modify', 'change',
                'edit.*task', 'edit', 'update.*title', 'update.*description', 'update.*priority',
                'change.*title', 'change.*description', 'change.*priority', 'modify.*title',
                'modify.*description', 'modify.*priority'
            ],
            IntentType.DELETE_TASK: [
                'delete.*task', 'remove.*task', 'drop.*task', 'delete', 'remove'
            ],
            IntentType.LIST_TASKS: [
                'show.*task', 'list.*task', 'view.*task', 'what.*task', 'all.*task', 'show', 'list'
            ],
            IntentType.SEARCH_TASKS: [
                'find.*task', 'search.*task', 'look.*for.*task', 'find', 'search'
            ],
            IntentType.FILTER_TASKS: [
                'filter.*task', 'show.*only', 'only.*task', 'just.*task', 'display.*only', 'filtered.*task', 'filter'
            ],
            IntentType.COMPLETE_TASK: [
                'complete.*task', 'finish.*task', 'done.*with.*task', 'mark.*done', 'complete', 'finish', 'done'
            ],
            IntentType.GET_USER_INFO: [
                'who.*am.*i', 'what.*is.*my.*email', 'my.*info', 'user.*info', 'who.*i.*am',
                'my.*name', 'what.*is.*my.*name', 'my.*email', 'what.*is.*my.*email'
            ]
        }

        best_intent = IntentType.UNKNOWN
        best_score = 0.0

        for intent, patterns in intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 1

            if score > best_score:
                best_score = score
                best_intent = intent

        # Normalize score to 0-1 range
        if best_score > 0:
            confidence = min(best_score / len(intent_patterns[best_intent]), 1.0)
        else:
            confidence = 0.0

        return best_intent, confidence

    def classify_multiple_intents(self, text: str) -> List[Tuple[IntentType, float]]:
        """
        Classify multiple possible intents from the same text
        """
        # For now, just return the primary intent
        primary_intent, confidence = self.classify_intent(text)
        return [(primary_intent, confidence)]


# Global instance for reuse
intent_classifier = IntentClassifier()