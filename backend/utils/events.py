import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
import asyncio
from fastapi import HTTPException
import os

# Get DAPR_HTTP_PORT from environment, default to 3500
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")

class DaprEventPublisher:
    """
    Utility class for publishing events to Dapr pub/sub component
    """
    
    def __init__(self, dapr_http_port: str = DAPR_HTTP_PORT):
        self.dapr_http_port = dapr_http_port
        self.dapr_base_url = f"http://localhost:{self.dapr_http_port}"
        
    async def publish_event(self, topic: str, data: Dict[str, Any], event_type: str = "custom", 
                           source: str = "/backend/tasks") -> bool:
        """
        Publish an event to a Dapr pub/sub topic
        
        Args:
            topic: The topic name to publish to (e.g., "task.created")
            data: The event payload data
            event_type: The event type (defaults to "custom")
            source: The event source (defaults to "/backend/tasks")
            
        Returns:
            bool: True if event was published successfully, False otherwise
        """
        try:
            # Create CloudEvent compliant payload
            event_payload = {
                "specversion": "1.0",
                "type": event_type,
                "source": source,
                "id": str(uuid.uuid4()),
                "time": datetime.utcnow().isoformat() + "Z",
                "datacontenttype": "application/json",
                "data": data
            }
            
            # Construct the URL for publishing to the pubsub component
            url = f"{self.dapr_base_url}/v1.0/publish/pubsub/{topic}"
            
            # Publish the event using httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=url,
                    json=event_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print(f"Dapr event published successfully to topic '{topic}'")
                    return True
                else:
                    print(f"Failed to publish Dapr event to topic '{topic}'. Status: {response.status_code}, Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Error publishing Dapr event to topic '{topic}': {str(e)}")
            return False

# Global instance of the publisher
dapr_publisher = DaprEventPublisher()

# Convenience functions for specific task events
async def publish_task_created_event(task_id: str, user_id: str, title: str, description: Optional[str] = None) -> bool:
    """Publish a task.created event"""
    data = {
        "task_id": task_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "timestamp": datetime.utcnow().isoformat()
    }
    return await dapr_publisher.publish_event("task.created", data, "task.created")

async def publish_task_updated_event(task_id: str, user_id: str, updated_fields: Dict[str, Any]) -> bool:
    """Publish a task.updated event"""
    data = {
        "task_id": task_id,
        "user_id": user_id,
        "updated_fields": updated_fields,
        "timestamp": datetime.utcnow().isoformat()
    }
    return await dapr_publisher.publish_event("task.updated", data, "task.updated")

async def publish_task_deleted_event(task_id: str, user_id: str) -> bool:
    """Publish a task.deleted event"""
    data = {
        "task_id": task_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    return await dapr_publisher.publish_event("task.deleted", data, "task.deleted")

async def publish_task_completed_event(task_id: str, user_id: str, completed: bool) -> bool:
    """Publish a task.completed event"""
    data = {
        "task_id": task_id,
        "user_id": user_id,
        "completed": completed,
        "timestamp": datetime.utcnow().isoformat()
    }
    return await dapr_publisher.publish_event("task.completed", data, "task.completed")