import re
from typing import Dict, List, Tuple
from ai_chatbot.services.cohere_client import CohereClient
from ai_chatbot.utils.logging import logger


class EntityExtractor:
    """
    Extracts entities from user input for the AI chatbot
    """

    def __init__(self):
        self.cohere_client = CohereClient()

    def extract_entities(self, text: str) -> Dict[str, str]:
        """
        Extract entities from the given text
        """
        try:
            # First try Cohere extraction if API key is available
            if self.cohere_client.client:
                cohere_entities = self.cohere_client.extract_entities(text)
                if cohere_entities:
                    return cohere_entities

            # Fall back to rule-based extraction
            return self._rule_based_extract(text)
        except Exception as e:
            logger.error(f"Error in entity extraction: {str(e)}", text=text)
            # Return empty dict if extraction fails
            return self._rule_based_extract(text)

    def _rule_based_extract(self, text: str) -> Dict[str, str]:
        """
        Rule-based entity extraction as fallback
        """
        entities = {}

        # Extract user info request types
        text_lower = text.lower()
        if 'my name' in text_lower or 'what is my name' in text_lower or 'tell me my name' in text_lower:
            entities['info_type'] = 'name'
        elif 'my email' in text_lower or 'what is my email' in text_lower or 'tell me my email' in text_lower:
            entities['info_type'] = 'email'
        elif 'my info' in text_lower or 'user info' in text_lower or 'who am i' in text_lower:
            entities['info_type'] = 'general'

        # Extract task titles (common phrases after verbs like "add", "create", "buy", etc.)
        add_patterns = [
            r'(?:add|create|make|buy|do|complete|finish)\s+(?:a\s+)?(?:task\s+to\s+|to\s+|that\s+)([^.!?]+?)(?:\.|$)',
            r'(?:add|create|make|buy|do|complete|finish)\s+(?:a\s+)?([^!.?]+?)(?:\.|$)'
        ]

        for pattern in add_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                task_title = match.group(1).strip()
                # Clean up the title
                task_title = re.sub(r'\s+', ' ', task_title)  # Replace multiple spaces with single space
                entities['task_title'] = task_title
                break

        # Extract update patterns - for changing specific attributes of tasks
        update_patterns = [
            r'(?:update|change|modify)\s+(?:the\s+)?(\w+)\s+of\s+(?:task|the)\s+(.*?)(?:\s+to|\s+as)\s+(.+?)(?:\.|$)',
            r'(?:update|change|modify)\s+(?:the\s+)?(\w+)\s+(?:to|as)\s+(.+?)(?:\.|$)',
            r'(?:update|change|modify)\s+(?:task\s+)?(.+?)\s+(?:title|name)\s+(?:to|as)\s+(.+?)(?:\.|$)',
            r'(?:update|change|modify)\s+(?:task\s+)?(.+?)\s+(?:description)\s+(?:to|as)\s+(.+?)(?:\.|$)',
            r'(?:update|change|modify)\s+(?:task\s+)?(.+?)\s+(?:priority)\s+(?:to|as)\s+(.+?)(?:\.|$)',
            r'(?:update|change|modify)\s+(?:task\s+)?(.+?)\s+(?:due date|date)\s+(?:to|as)\s+(.+?)(?:\.|$)',
        ]

        for pattern in update_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    # Pattern like "update priority of task X to Y" or "update X priority to Y"
                    if len(match.groups()) == 3:
                        attr = match.group(1).strip()
                        search_term = match.group(2).strip()
                        new_value = match.group(3).strip()
                    elif len(match.groups()) == 2:
                        # Pattern like "update title to X" or "change priority to Y"
                        attr = match.group(1).strip()
                        new_value = match.group(2).strip()
                        search_term = entities.get('task_title', entities.get('search_term', ''))

                    # Map attribute names to the appropriate entity keys
                    attr_map = {
                        'title': 'title',
                        'name': 'title',
                        'description': 'description',
                        'priority': 'priority',
                        'due date': 'due_date',
                        'date': 'due_date',
                        'category': 'category'
                    }

                    if attr.lower() in attr_map:
                        entities[attr_map[attr.lower()]] = new_value

                    if search_term:
                        entities['search_term'] = search_term
                break

        # Extract search terms
        search_patterns = [
            r'(?:find|search|look.*for|show.*me).*?(?:tasks?|items?)\s+(?:containing|about|with|like)\s+([^!.?]+?)(?:\.|$)',
            r'(?:find|search|look.*for|show.*me)\s+([^!.?]+?)(?:\.|$)'
        ]

        for pattern in search_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                search_term = match.group(1).strip()
                search_term = re.sub(r'\s+', ' ', search_term)
                entities['search_term'] = search_term
                break

        # Extract task identifiers (if mentioned by title or partial title)
        if 'task_title' not in entities and 'search_term' in entities:
            entities['task_title'] = entities['search_term']

        # Extract priority if mentioned
        priority_words = ['high', 'medium', 'low']
        for priority in priority_words:
            if priority in text.lower():
                entities['priority'] = priority
                break

        # Extract due date if mentioned (basic pattern)
        date_patterns = [
            r'on\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'on\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,\s*\d{4})',
            r'today|tomorrow|next\s+week|next\s+month'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['due_date'] = match.group(0)
                break

        return entities

    def extract_task_details(self, text: str) -> Dict[str, str]:
        """
        Extract specific task-related details from text
        """
        entities = self.extract_entities(text)

        # Additional extraction specific to task details
        # Extract description if it exists separately
        desc_patterns = [
            r'description:\s*(.+?)(?:\.|$)',
            r'with\s+description\s+(.+?)(?:\.|$)',
            r'that\s+does\s+(.+?)(?:\.|$)'
        ]

        for pattern in desc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['description'] = match.group(1).strip()
                break

        return entities


# Global instance for reuse
entity_extractor = EntityExtractor()