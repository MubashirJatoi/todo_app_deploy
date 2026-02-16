import requests
from typing import Dict, List, Optional, Any
from ai_chatbot.config import config
import json
from ai_chatbot.user_context.agent import user_context_agent


class Phase2APIClient:
    """
    Client for interacting with Phase 2 API endpoints
    """

    def __init__(self):
        self.base_url = config.PHASE2_API_BASE_URL
        self.timeout = config.PHASE2_API_TIMEOUT

    def _make_request(self, method: str, endpoint: str, headers: Dict, json_data: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Phase 2 API
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json_data, timeout=self.timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=json_data, timeout=self.timeout)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, json=json_data, timeout=self.timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling Phase 2 API: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error calling Phase 2 API: {str(e)}")

    def get_user_tasks(self, user_id: str, auth_token: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get tasks for a specific user
        """
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        # Build query parameters
        params = filters or {}
        param_str = "&".join([f"{k}={v}" for k, v in params.items() if v is not None])
        endpoint = f"/api/tasks"
        if param_str:
            endpoint += f"?{param_str}"

        response = self._make_request("GET", endpoint, headers)
        return response.get("tasks", [])

    def create_task(self, user_id: str, auth_token: str, task_data: Dict) -> Dict:
        """
        Create a new task for a user
        """
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        response = self._make_request("POST", "/api/tasks/", headers, task_data)
        return response

    def update_task(self, user_id: str, auth_token: str, task_id: str, task_data: Dict) -> Dict:
        """
        Update a specific task for a user
        """
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        response = self._make_request("PUT", f"/api/tasks/{task_id}", headers, task_data)
        return response

    def delete_task(self, user_id: str, auth_token: str, task_id: str) -> bool:
        """
        Delete a specific task for a user
        """
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        try:
            self._make_request("DELETE", f"/api/tasks/{task_id}", headers)
            return True
        except Exception:
            return False

    def toggle_task_completion(self, user_id: str, auth_token: str, task_id: str, completed: bool) -> Dict:
        """
        Toggle completion status of a task
        """
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        data = {"completed": completed}
        response = self._make_request("PATCH", f"/api/tasks/{task_id}/complete", headers, data)
        return response

    def get_user_info(self, user_id: str, auth_token: str) -> Dict:
        """
        Get user information from the database for the logged-in user
        """
        # Use the user context agent to fetch user information from the database
        user_info = user_context_agent.get_user_info(auth_token)

        if user_info and user_info.get("authenticated"):
            return {
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "user_id": user_info.get("user_id"),
                "authenticated": True
            }
        else:
            return {
                "authenticated": False,
                "error": user_info.get("error", "Authentication failed")
            }

    def get_task_by_id(self, user_id: str, auth_token: str, task_id: str) -> Optional[Dict]:
        """
        Get a specific task by ID
        """
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        try:
            response = self._make_request("GET", f"/api/tasks/{task_id}", headers)
            return response
        except Exception:
            return None


# Global instance for reuse
phase2_client = Phase2APIClient()