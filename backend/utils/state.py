import json
import httpx
from typing import Any, Dict, Optional
import os

# Get DAPR_HTTP_PORT from environment, default to 3500
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")

class DaprStateStore:
    """
    Utility class for managing state with Dapr state store
    """
    
    def __init__(self, dapr_http_port: str = DAPR_HTTP_PORT, state_store_name: str = "statestore"):
        self.dapr_http_port = dapr_http_port
        self.dapr_base_url = f"http://localhost:{self.dapr_http_port}"
        self.state_store_name = state_store_name
        
    async def save_state(self, key: str, value: Any, ttl_in_seconds: Optional[int] = None) -> bool:
        """
        Save state to Dapr state store
        
        Args:
            key: The state key
            value: The state value (will be JSON serialized)
            ttl_in_seconds: Time-to-live in seconds (optional)
            
        Returns:
            bool: True if state was saved successfully, False otherwise
        """
        try:
            # Prepare the state entry
            state_entry = {
                "key": key,
                "value": value
            }
            
            # Add TTL metadata if specified
            if ttl_in_seconds is not None:
                state_entry["metadata"] = {
                    "ttlInSeconds": str(ttl_in_seconds)
                }
            
            # Construct the URL for saving to the state store
            url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}"
            
            # Save the state using httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=url,
                    json=[state_entry],  # Dapr expects an array of state entries
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 204]:
                    print(f"Dapr state saved successfully with key '{key}'")
                    return True
                else:
                    print(f"Failed to save Dapr state with key '{key}'. Status: {response.status_code}, Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Error saving Dapr state with key '{key}': {str(e)}")
            return False
    
    async def get_state(self, key: str) -> Optional[Any]:
        """
        Get state from Dapr state store
        
        Args:
            key: The state key
            
        Returns:
            The state value if found, None otherwise
        """
        try:
            # Construct the URL for getting from the state store
            url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}/{key}"
            
            # Get the state using httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(url=url)
                
                if response.status_code == 200:
                    print(f"Dapr state retrieved successfully with key '{key}'")
                    return response.json()
                elif response.status_code == 404:
                    print(f"Dapr state not found with key '{key}'")
                    return None
                else:
                    print(f"Failed to get Dapr state with key '{key}'. Status: {response.status_code}, Response: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"Error getting Dapr state with key '{key}': {str(e)}")
            return None
    
    async def delete_state(self, key: str) -> bool:
        """
        Delete state from Dapr state store
        
        Args:
            key: The state key
            
        Returns:
            bool: True if state was deleted successfully, False otherwise
        """
        try:
            # Construct the URL for deleting from the state store
            url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}/{key}"
            
            # Delete the state using httpx
            async with httpx.AsyncClient() as client:
                response = await client.delete(url=url)
                
                if response.status_code in [200, 204]:
                    print(f"Dapr state deleted successfully with key '{key}'")
                    return True
                else:
                    print(f"Failed to delete Dapr state with key '{key}'. Status: {response.status_code}, Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Error deleting Dapr state with key '{key}': {str(e)}")
            return False

# Global instance of the state store
dapr_state_store = DaprStateStore()

# Convenience functions for specific use cases
async def save_chat_session(user_id: str, session_data: Dict[str, Any], ttl_in_seconds: int = 3600) -> bool:
    """Save chat session data to Dapr state store with TTL"""
    key = f"chat:session:{user_id}"
    return await dapr_state_store.save_state(key, session_data, ttl_in_seconds)

async def get_chat_session(user_id: str) -> Optional[Dict[str, Any]]:
    """Get chat session data from Dapr state store"""
    key = f"chat:session:{user_id}"
    return await dapr_state_store.get_state(key)

async def delete_chat_session(user_id: str) -> bool:
    """Delete chat session data from Dapr state store"""
    key = f"chat:session:{user_id}"
    return await dapr_state_store.delete_state(key)

async def save_user_cache(user_id: str, user_data: Dict[str, Any], ttl_in_seconds: int = 1800) -> bool:
    """Save user data to cache in Dapr state store"""
    key = f"cache:user:{user_id}"
    return await dapr_state_store.save_state(key, user_data, ttl_in_seconds)

async def get_user_cache(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user data from cache in Dapr state store"""
    key = f"cache:user:{user_id}"
    return await dapr_state_store.get_state(key)

async def save_task_list_cache(user_id: str, task_list: list, ttl_in_seconds: int = 300) -> bool:
    """Save task list to cache in Dapr state store"""
    key = f"cache:tasks:{user_id}"
    return await dapr_state_store.save_state(key, task_list, ttl_in_seconds)

async def get_task_list_cache(user_id: str) -> Optional[list]:
    """Get task list from cache in Dapr state store"""
    key = f"cache:tasks:{user_id}"
    return await dapr_state_store.get_state(key)