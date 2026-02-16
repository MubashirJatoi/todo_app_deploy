# Dapr Service Invocation Skill

## Purpose
Implement service-to-service communication using Dapr service invocation API.

## What it does
- Converts direct HTTP calls to Dapr service invocation
- Implements service discovery using Dapr app-id
- Adds built-in retry, timeout, and circuit breaker capabilities
- Propagates headers and correlation IDs across services
- Handles error responses from invoked services

## What it does NOT do
- Configure Dapr sidecars or components
- Implement asynchronous event-driven patterns (use pub/sub for that)
- Handle direct database access

## Usage
Use this skill when you need to:
- Replace hardcoded service URLs with Dapr invocation
- Implement resilient service-to-service calls
- Add service discovery without external dependencies
- Propagate distributed tracing across service boundaries

## Example (Python)
```python
import httpx

async def call_backend_service(method: str, data: dict):
    dapr_url = "http://localhost:3500"
    app_id = "backend-app"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{dapr_url}/v1.0/invoke/{app_id}/method/{method}",
            json=data,
            headers={"dapr-app-id": app_id}
        )
        return response.json()
```

## Example (Next.js/TypeScript)
```typescript
async function invokeDaprService(appId: string, method: string) {
  const daprPort = process.env.DAPR_HTTP_PORT || '3500';
  const response = await fetch(
    `http://localhost:${daprPort}/v1.0/invoke/${appId}/method/${method}`
  );
  return response.json();
}
```
