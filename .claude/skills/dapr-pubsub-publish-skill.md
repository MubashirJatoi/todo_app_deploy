# Dapr Pub/Sub Publish Skill

## Purpose
Implement event publishing logic in application code using Dapr pub/sub API.

## What it does
- Publishes events to Dapr pub/sub topics via HTTP or gRPC
- Formats events using CloudEvents standard
- Adds event metadata (timestamp, correlation ID, source)
- Handles publish failures and retries
- Implements event batching when appropriate

## What it does NOT do
- Create or configure pub/sub components (YAML manifests)
- Subscribe to or handle incoming events
- Manage message broker infrastructure

## Usage
Use this skill when you need to:
- Add event publishing to existing application endpoints
- Convert synchronous operations to publish events instead
- Implement fire-and-forget event patterns
- Add correlation IDs and tracing to published events

## Example (Python/FastAPI)
```python
import httpx
import uuid
from datetime import datetime

async def publish_task_created(task_id: int, user_id: int):
    event = {
        "specversion": "1.0",
        "type": "com.todo.task.created",
        "source": "/backend/tasks",
        "id": str(uuid.uuid4()),
        "time": datetime.utcnow().isoformat() + "Z",
        "data": {
            "task_id": task_id,
            "user_id": user_id
        }
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/publish/pubsub/task.created",
            json=event
        )
```
