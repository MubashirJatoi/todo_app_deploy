# Dapr State Management Skill

## Purpose
Implement distributed state management using Dapr state store API in application code.

## What it does
- Implements state save/get/delete operations via Dapr HTTP/gRPC
- Handles state with TTL (time-to-live) for temporary data
- Implements ETag-based optimistic concurrency control
- Performs bulk state operations for efficiency
- Manages state key naming conventions
- Implements caching strategies using state store

## What it does NOT do
- Create or configure state store components (YAML)
- Manage the underlying state store infrastructure (Redis, PostgreSQL)
- Implement business logic unrelated to state management

## Usage
Use this skill when you need to:
- Store and retrieve application state via Dapr
- Implement session management with TTL
- Cache frequently accessed data
- Store temporary workflow state
- Migrate from direct database access to Dapr state store

## Example (Python)
```python
import httpx

async def save_state(key: str, value: dict, ttl_seconds: int = None):
    url = "http://localhost:3500/v1.0/state/statestore"

    state_data = [{
        "key": key,
        "value": value,
        "metadata": {"ttlInSeconds": str(ttl_seconds)} if ttl_seconds else {}
    }]

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=state_data)
        return response.status_code == 204

async def get_state(key: str):
    url = f"http://localhost:3500/v1.0/state/statestore/{key}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 204:
            return None
        return response.json()

async def delete_state(key: str):
    url = f"http://localhost:3500/v1.0/state/statestore/{key}"

    async with httpx.AsyncClient() as client:
        response = await client.delete(url)
        return response.status_code == 204
```

## Key Naming Convention
```
<domain>:<type>:<identifier>

Examples:
- chat:session:123 (chat session for user 123)
- cache:tasks:456 (cached tasks for user 456)
- workflow:create-task:789 (workflow state)
```
