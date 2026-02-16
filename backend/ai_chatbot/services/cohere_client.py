import cohere
from typing import Dict, List, Optional
from ai_chatbot.config import config


class CohereClient:
    """
    Wrapper class for Cohere API functionality
    """

    def __init__(self):
        if not config.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable is required")

        self.client = cohere.Client(config.COHERE_API_KEY)

    def generate_text(self, prompt: str, max_tokens: int = 100) -> str:
        """
        Generate text based on the provided prompt
        """
        try:
            response = self.client.generate(
                model='command',
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.7
            )

            if response.generations:
                return response.generations[0].text.strip()
            else:
                return ""
        except Exception as e:
            print(f"Error calling Cohere API: {e}")
            return ""

    def classify_intent(self, text: str, possible_intents: List[str]) -> str:
        """
        Classify the intent of the given text
        """
        try:
            # Prepare examples for classification
            examples = []
            for intent in possible_intents:
                # Create example text for each intent
                if intent == "CREATE_TASK":
                    examples.extend([
                        {"text": "add a task to buy groceries", "label": "CREATE_TASK"},
                        {"text": "create a new task for meeting prep", "label": "CREATE_TASK"},
                        {"text": "make a task to call mom", "label": "CREATE_TASK"}
                    ])
                elif intent == "UPDATE_TASK":
                    examples.extend([
                        {"text": "mark my meeting prep task as done", "label": "UPDATE_TASK"},
                        {"text": "complete the grocery task", "label": "UPDATE_TASK"},
                        {"text": "finish the assignment", "label": "UPDATE_TASK"}
                    ])
                elif intent == "DELETE_TASK":
                    examples.extend([
                        {"text": "delete the old task", "label": "DELETE_TASK"},
                        {"text": "remove the meeting task", "label": "DELETE_TASK"},
                        {"text": "drop the assignment", "label": "DELETE_TASK"}
                    ])
                elif intent == "LIST_TASKS":
                    examples.extend([
                        {"text": "show me my tasks", "label": "LIST_TASKS"},
                        {"text": "what tasks do I have", "label": "LIST_TASKS"},
                        {"text": "list all tasks", "label": "LIST_TASKS"}
                    ])
                elif intent == "SEARCH_TASKS":
                    examples.extend([
                        {"text": "find tasks about work", "label": "SEARCH_TASKS"},
                        {"text": "search for project tasks", "label": "SEARCH_TASKS"},
                        {"text": "look for homework", "label": "SEARCH_TASKS"}
                    ])

            response = self.client.classify(
                model='large',
                inputs=[text],
                examples=examples
            )

            if response.classifications and len(response.classifications) > 0:
                return response.classifications[0].prediction
            else:
                return "UNKNOWN"
        except Exception as e:
            print(f"Error calling Cohere classification API: {e}")
            return "UNKNOWN"

    def extract_entities(self, text: str) -> Dict[str, str]:
        """
        Extract entities from the given text using generative prompting
        """
        try:
            prompt = f"""
            Extract the following entities from the text below. Return in JSON format:
            - task_title: The title of the task if mentioned
            - search_query: The search query if mentioned
            - task_id: The task ID if mentioned

            Text: "{text}"

            JSON Response:
            """

            response = self.client.generate(
                model='command',
                prompt=prompt,
                max_tokens=100,
                temperature=0.3
            )

            if response.generations:
                # This is a simplified approach - in a real implementation,
                # you'd want to properly parse the JSON response
                extracted_text = response.generations[0].text.strip()

                # Basic parsing to extract entities
                entities = {}

                # If we have a JSON-like response, try to parse it
                if "{" in extracted_text and "}" in extracted_text:
                    # Simplified parsing - in reality you'd want proper JSON parsing
                    if '"task_title"' in extracted_text:
                        # Extract the value after "task_title":
                        start = extracted_text.find('"task_title"') + len('"task_title"')
                        start = extracted_text.find(':', start)
                        if start != -1:
                            start = extracted_text.find('"', start)
                            if start != -1:
                                end = extracted_text.find('"', start + 1)
                                if end != -1:
                                    entities['task_title'] = extracted_text[start + 1:end]

                return entities
            else:
                return {}
        except Exception as e:
            print(f"Error calling Cohere entity extraction API: {e}")
            return {}