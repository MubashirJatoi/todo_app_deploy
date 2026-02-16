from typing import Dict, Any, Optional
from ai_chatbot.services.phase2_client import phase2_client
from ai_chatbot.utils.logging import logger
from ai_chatbot.models.command import NaturalLanguageCommand


class BackendIntegrationAgent:
    """
    Agent responsible for integrating with the backend Phase 2 API
    """

    def __init__(self):
        self.phase2_client = phase2_client

    def call_phase2_api(self, endpoint: str, method: str, auth_token: str, user_id: str, data: Dict = None) -> Dict[str, Any]:
        """
        Make a call to the Phase 2 API
        """
        try:
            logger.log_api_call(
                service="Phase2 API",
                endpoint=endpoint,
                success=True
            )

            # Route the call based on the endpoint
            if endpoint == "/api/tasks" and method == "GET":
                return self.phase2_client.get_user_tasks(user_id, auth_token)
            elif endpoint == "/api/tasks/" and method == "POST":
                return self.phase2_client.create_task(user_id, auth_token, data)
            elif endpoint.startswith("/api/tasks/") and method == "GET":
                # Extract task ID from endpoint
                task_id = endpoint.split("/")[-1]
                return self.phase2_client.get_task_by_id(user_id, auth_token, task_id)
            elif endpoint.startswith("/api/tasks/") and method == "PUT":
                # Extract task ID from endpoint
                task_id = endpoint.split("/")[-1]
                return self.phase2_client.update_task(user_id, auth_token, task_id, data)
            elif endpoint.startswith("/api/tasks/") and method == "DELETE":
                # Extract task ID from endpoint
                task_id = endpoint.split("/")[-1]
                return {"success": self.phase2_client.delete_task(user_id, auth_token, task_id)}
            elif endpoint.startswith("/api/tasks/") and method == "PATCH" and "complete" in endpoint:
                # Handle task completion
                task_id = endpoint.split("/")[2]  # Extract task ID from "/api/tasks/{id}/complete"
                completed = data.get("completed", True) if data else True
                return self.phase2_client.toggle_task_completion(user_id, auth_token, task_id, completed)
            else:
                raise ValueError(f"Unsupported endpoint/method combination: {endpoint}, {method}")

        except Exception as e:
            logger.error(f"Error calling Phase 2 API: {str(e)}",
                         endpoint=endpoint,
                         method=method,
                         user_id=user_id)
            raise

    def execute_task_operation(self, command: NaturalLanguageCommand, auth_token: str) -> Dict[str, Any]:
        """
        Execute a task operation based on the natural language command
        """
        try:
            user_id = str(command.user_id)

            if command.intent.value == "CREATE_TASK":
                # Prepare task data from command entities
                task_data = {
                    "title": command.entities.get("task_title", ""),
                    "description": command.entities.get("description", ""),
                    "priority": command.entities.get("priority", "medium")
                }

                if "due_date" in command.entities:
                    task_data["due_date"] = command.entities["due_date"]

                return self.call_phase2_api("/api/tasks/", "POST", auth_token, user_id, task_data)

            elif command.intent.value in ["UPDATE_TASK", "COMPLETE_TASK"]:
                # For updates, we need to find the task first, then update it
                search_term = command.entities.get("task_title") or command.entities.get("search_term")

                if search_term:
                    # First get the tasks to find the matching one
                    tasks = self.call_phase2_api("/api/tasks", "GET", auth_token, user_id)
                    matching_task = None

                    for task in tasks.get("tasks", []):
                        if search_term.lower() in task.get("title", "").lower():
                            matching_task = task
                            break

                    if matching_task:
                        task_id = matching_task["id"]

                        if command.intent.value == "COMPLETE_TASK":
                            # Toggle completion
                            update_data = {"completed": True}
                            return self.call_phase2_api(f"/api/tasks/{task_id}", "PATCH", auth_token, user_id, update_data)
                        else:
                            # Regular update
                            update_data = {}
                            if "title" in command.entities:
                                update_data["title"] = command.entities["title"]
                            if "description" in command.entities:
                                update_data["description"] = command.entities["description"]
                            if "priority" in command.entities:
                                update_data["priority"] = command.entities["priority"]

                            return self.call_phase2_api(f"/api/tasks/{task_id}", "PUT", auth_token, user_id, update_data)
                    else:
                        return {"error": f"No task found matching '{search_term}'", "success": False}
                else:
                    return {"error": "No task specified to update", "success": False}

            elif command.intent.value == "DELETE_TASK":
                # Find and delete the task
                search_term = command.entities.get("task_title") or command.entities.get("search_term")

                if search_term:
                    tasks = self.call_phase2_api("/api/tasks", "GET", auth_token, user_id)
                    matching_task = None

                    for task in tasks.get("tasks", []):
                        if search_term.lower() in task.get("title", "").lower():
                            matching_task = task
                            break

                    if matching_task:
                        task_id = matching_task["id"]
                        result = self.call_phase2_api(f"/api/tasks/{task_id}", "DELETE", auth_token, user_id)
                        return {"success": result.get("success", False), "task_id": task_id}
                    else:
                        return {"error": f"No task found matching '{search_term}'", "success": False}
                else:
                    return {"error": "No task specified to delete", "success": False}

            elif command.intent.value == "LIST_TASKS":
                # Get all tasks for the user
                return self.call_phase2_api("/api/tasks", "GET", auth_token, user_id)

            elif command.intent.value == "SEARCH_TASKS":
                search_term = command.entities.get("search_term", "")
                # In a real implementation, we might need to filter on the client side
                # or make a more specific API call if the backend supports it
                all_tasks = self.call_phase2_api("/api/tasks", "GET", auth_token, user_id)

                if search_term:
                    # Filter tasks based on search term
                    filtered_tasks = []
                    for task in all_tasks.get("tasks", []):
                        if (search_term.lower() in task.get("title", "").lower() or
                            search_term.lower() in task.get("description", "").lower()):
                            filtered_tasks.append(task)
                    return {"tasks": filtered_tasks}
                else:
                    return all_tasks
            else:
                return {"error": f"Unsupported command intent: {command.intent.value}", "success": False}

        except Exception as e:
            logger.error(f"Error executing task operation: {str(e)}",
                         command=command.dict(),
                         user_id=user_id)
            return {"error": str(e), "success": False}

    def validate_backend_connection(self) -> bool:
        """
        Validate that we can connect to the backend Phase 2 API
        """
        try:
            # Try a simple operation to validate connectivity
            # For now, we'll just check if the client is initialized properly
            return self.phase2_client is not None
        except Exception as e:
            logger.error(f"Error validating backend connection: {str(e)}")
            return False


# Global instance for reuse
backend_integration_agent = BackendIntegrationAgent()