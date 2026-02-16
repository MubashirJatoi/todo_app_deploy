from typing import Dict, Any, Optional
from ai_chatbot.services.phase2_client import phase2_client
from ai_chatbot.utils.logging import logger
from ai_chatbot.models.command import NaturalLanguageCommand


class Phase2APIHandlers:
    """
    Handlers for making specific Phase 2 API calls
    """

    def __init__(self):
        self.phase2_client = phase2_client

    def handle_get_tasks(self, user_id: str, auth_token: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Handle getting tasks from Phase 2 API
        """
        try:
            tasks = self.phase2_client.get_user_tasks(user_id, auth_token, filters or {})

            logger.log_api_call(
                service="Phase2 API",
                endpoint="/api/tasks",
                success=True,
                duration_ms=None
            )

            return {
                "success": True,
                "data": {"tasks": tasks},
                "message": f"Retrieved {len(tasks)} tasks"
            }
        except Exception as e:
            logger.error(f"Error getting tasks: {str(e)}",
                         user_id=user_id)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve tasks"
            }

    def handle_create_task(self, user_id: str, auth_token: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle creating a task via Phase 2 API
        """
        try:
            result = self.phase2_client.create_task(user_id, auth_token, task_data)

            logger.log_api_call(
                service="Phase2 API",
                endpoint="/api/tasks",
                success=True,
                duration_ms=None
            )

            return {
                "success": True,
                "data": {"task": result},
                "message": f"Task '{result.get('title', 'Unknown')}' created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}",
                         user_id=user_id,
                         task_data=task_data)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create task"
            }

    def handle_update_task(self, user_id: str, auth_token: str, task_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle updating a task via Phase 2 API
        """
        try:
            result = self.phase2_client.update_task(user_id, auth_token, task_id, update_data)

            logger.log_api_call(
                service="Phase2 API",
                endpoint=f"/api/tasks/{task_id}",
                success=True,
                duration_ms=None
            )

            return {
                "success": True,
                "data": {"task": result},
                "message": f"Task '{result.get('title', 'Unknown')}' updated successfully"
            }
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}",
                         user_id=user_id,
                         task_id=task_id,
                         update_data=update_data)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update task"
            }

    def handle_delete_task(self, user_id: str, auth_token: str, task_id: str) -> Dict[str, Any]:
        """
        Handle deleting a task via Phase 2 API
        """
        try:
            success = self.phase2_client.delete_task(user_id, auth_token, task_id)

            logger.log_api_call(
                service="Phase2 API",
                endpoint=f"/api/tasks/{task_id}",
                success=success,
                duration_ms=None
            )

            if success:
                return {
                    "success": True,
                    "data": {"task_id": task_id},
                    "message": f"Task {task_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to delete task {task_id}"
                }
        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}",
                         user_id=user_id,
                         task_id=task_id)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete task"
            }

    def handle_toggle_task_completion(self, user_id: str, auth_token: str, task_id: str, completed: bool) -> Dict[str, Any]:
        """
        Handle toggling task completion via Phase 2 API
        """
        try:
            result = self.phase2_client.toggle_task_completion(user_id, auth_token, task_id, completed)

            logger.log_api_call(
                service="Phase2 API",
                endpoint=f"/api/tasks/{task_id}/complete",
                success=True,
                duration_ms=None
            )

            status = "completed" if completed else "marked as incomplete"
            return {
                "success": True,
                "data": {"task": result},
                "message": f"Task '{result.get('title', 'Unknown')}' {status} successfully"
            }
        except Exception as e:
            logger.error(f"Error toggling task completion: {str(e)}",
                         user_id=user_id,
                         task_id=task_id,
                         completed=completed)
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to {'' if completed else 'mark as '}complete task"
            }

    def handle_get_task_by_id(self, user_id: str, auth_token: str, task_id: str) -> Dict[str, Any]:
        """
        Handle getting a specific task by ID via Phase 2 API
        """
        try:
            result = self.phase2_client.get_task_by_id(user_id, auth_token, task_id)

            logger.log_api_call(
                service="Phase2 API",
                endpoint=f"/api/tasks/{task_id}",
                success=result is not None,
                duration_ms=None
            )

            if result:
                return {
                    "success": True,
                    "data": {"task": result},
                    "message": f"Retrieved task '{result.get('title', 'Unknown')}'"
                }
            else:
                return {
                    "success": False,
                    "message": f"Task {task_id} not found"
                }
        except Exception as e:
            logger.error(f"Error getting task by ID: {str(e)}",
                         user_id=user_id,
                         task_id=task_id)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve task"
            }

    def handle_search_tasks(self, user_id: str, auth_token: str, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle searching tasks via Phase 2 API
        """
        try:
            tasks = self.phase2_client.get_user_tasks(user_id, auth_token, search_params)

            logger.log_api_call(
                service="Phase2 API",
                endpoint="/api/tasks",
                success=True,
                duration_ms=None
            )

            return {
                "success": True,
                "data": {"tasks": tasks},
                "message": f"Found {len(tasks)} matching tasks"
            }
        except Exception as e:
            logger.error(f"Error searching tasks: {str(e)}",
                         user_id=user_id,
                         search_params=search_params)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to search tasks"
            }


# Global instance for reuse
phase2_api_handlers = Phase2APIHandlers()