# Dapr Pub/Sub Subscribe Skill

## Purpose
Implement event subscriber handlers in application code using Dapr pub/sub API.

## What it does
- Creates subscription configuration endpoints (/dapr/subscribe)
- Implements event handler endpoints for subscribed topics
- Handles incoming CloudEvents with proper parsing
- Implements idempotent event processing
- Returns SUCCESS/RETRY/DROP status codes based on processing result

## What it does NOT do
- Publish events to topics
- Create or configure pub/sub components
- Implement business logic (separate from event handling)

## Usage
Use this skill when you need to:
- Subscribe application to specific topics
- Handle incoming events from other services
- Implement event-driven workflows
- Process events asynchronously

## Example (Python/FastAPI)
```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "pubsub",
            "topic": "task.created",
            "route": "/events/task-created"
        }
    ]

@app.post("/events/task-created")
async def handle_task_created(request: Request):
    event = await request.json()
    event_id = event.get("id")

    # Check idempotency
    if await is_processed(event_id):
        return {"status": "SUCCESS"}

    # Process event
    try:
        await process_event(event["data"])
        await mark_processed(event_id)
        return {"status": "SUCCESS"}
    except Exception:
        return {"status": "RETRY"}
```
