# AI Chatbot API Contract

## Overview
This contract defines the API endpoints for the AI Todo Chatbot service that operates as a control layer on top of Phase 2 APIs.

## Base URL
`http://localhost:8001/chatbot` (or configured endpoint)

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt-token>
```

## Endpoints

### POST /chat
Process a natural language command from the user.

**Request:**
```json
{
  "message": "Add a task: Buy groceries",
  "user_id": "user-uuid-from-phase2",
  "session_id": "optional-session-id-for-context"
}
```

**Response (Success):**
```json
{
  "response": "Successfully added task: Buy groceries",
  "intent": "CREATE_TASK",
  "action_result": {
    "task_id": "new-task-uuid",
    "title": "Buy groceries",
    "completed": false
  },
  "timestamp": "2026-01-26T10:00:00Z"
}
```

**Response (Requires Clarification):**
```json
{
  "response": "Which task would you like to mark as complete? I found multiple tasks with similar names.",
  "requires_clarification": true,
  "options": [
    {"id": "task-1", "title": "Buy groceries for Monday"},
    {"id": "task-2", "title": "Buy groceries for party"}
  ],
  "intent": "UPDATE_TASK"
}
```

**Response (Confirmation Required):**
```json
{
  "response": "Are you sure you want to delete all your tasks? This action cannot be undone.",
  "requires_confirmation": true,
  "confirmation_token": "confirm-xyz-123",
  "intent": "DELETE_TASK"
}
```

**Response (Error):**
```json
{
  "error": "Invalid authentication token",
  "code": "AUTH_ERROR",
  "timestamp": "2026-01-26T10:00:00Z"
}
```

### POST /confirm
Confirm a previously requested action.

**Request:**
```json
{
  "confirmation_token": "confirm-xyz-123",
  "user_id": "user-uuid-from-phase2"
}
```

**Response:**
```json
{
  "response": "Tasks successfully deleted",
  "action_result": {
    "deleted_count": 5
  },
  "timestamp": "2026-01-26T10:00:00Z"
}
```

### GET /user-info
Get information about the authenticated user.

**Request Headers:**
```
Authorization: Bearer <valid-jwt-token>
```

**Response:**
```json
{
  "user_id": "user-uuid-from-phase2",
  "email": "user@example.com",
  "display_name": "John Doe",
  "created_at": "2026-01-01T00:00:00Z"
}
```

## Error Codes
- `AUTH_ERROR`: Invalid or expired authentication token
- `VALIDATION_ERROR`: Request data validation failed
- `INTENT_RECOGNITION_ERROR`: Could not understand user intent
- `ENTITY_EXTRACTION_ERROR`: Could not extract required entities
- `PHASE2_API_ERROR`: Error communicating with Phase 2 API
- `RATE_LIMIT_EXCEEDED`: Too many requests from user
- `UNSAFE_ACTION_BLOCKED`: Requested action violates safety rules

## Data Models

### Intent Types
- `CREATE_TASK`: Create a new task
- `UPDATE_TASK`: Update an existing task (title, description, status)
- `DELETE_TASK`: Delete one or more tasks
- `LIST_TASKS`: List tasks with optional filters
- `SEARCH_TASKS`: Search tasks by title or description
- `FILTER_TASKS`: Filter tasks by status or other criteria
- `SORT_TASKS`: Sort tasks by various attributes
- `GET_USER_INFO`: Retrieve user information

### Task Object
```json
{
  "id": "task-uuid",
  "title": "Task title",
  "description": "Optional task description",
  "completed": false,
  "created_at": "2026-01-26T10:00:00Z",
  "updated_at": "2026-01-26T10:00:00Z",
  "user_id": "user-uuid"
}
```

## Security Requirements
1. All requests must be authenticated
2. Users can only access their own data
3. Unsafe operations require explicit confirmation
4. Input validation must prevent injection attacks
5. Rate limiting must prevent abuse

## Performance Requirements
1. Response time under 2 seconds for 95% of requests
2. Maintain 99% uptime for AI services
3. Handle at least 100 concurrent users
4. Process natural language with 90%+ accuracy