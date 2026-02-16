# API Contracts: Phase II Todo Full-Stack Web Application

**Date**: 2026-01-14
**Feature**: 1-todo-web-app
**Input**: Functional requirements from feature spec

## Authentication

All endpoints except authentication endpoints require JWT token in Authorization header:
```
Authorization: Bearer {jwt_token}
```

## Endpoints

### Authentication Endpoints

#### POST /api/auth/register
Register a new user

**Request**:
```json
{
  "email": "user@example.com",
  "password": "secure_password_123",
  "name": "John Doe"
}
```

**Response 201 Created**:
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-01-14T10:00:00Z"
}
```

**Response 400 Bad Request**:
```json
{
  "error": "Invalid input",
  "details": ["Email format invalid", "Password too weak"]
}
```

**Response 409 Conflict**:
```json
{
  "error": "Email already registered"
}
```

#### POST /api/auth/login
Authenticate user and return JWT token

**Request**:
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Response 200 OK**:
```json
{
  "token": "jwt_token_string",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Response 401 Unauthorized**:
```json
{
  "error": "Invalid credentials"
}
```

### Task Management Endpoints

#### GET /api/tasks
Get all tasks for the authenticated user

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Response 200 OK**:
```json
{
  "tasks": [
    {
      "id": "uuid-string",
      "title": "Sample task",
      "description": "Sample description",
      "completed": false,
      "user_id": "user-uuid-string",
      "created_at": "2026-01-14T10:00:00Z",
      "updated_at": "2026-01-14T10:00:00Z"
    }
  ]
}
```

**Response 401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

#### POST /api/tasks
Create a new task for the authenticated user

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Request**:
```json
{
  "title": "New task title",
  "description": "Optional task description"
}
```

**Response 201 Created**:
```json
{
  "id": "uuid-string",
  "title": "New task title",
  "description": "Optional task description",
  "completed": false,
  "user_id": "authenticated-user-uuid",
  "created_at": "2026-01-14T10:00:00Z",
  "updated_at": "2026-01-14T10:00:00Z"
}
```

**Response 400 Bad Request**:
```json
{
  "error": "Invalid input",
  "details": ["Title is required", "Title too long"]
}
```

**Response 401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

#### GET /api/tasks/{id}
Get a specific task by ID

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Path Parameters**:
- id: Task UUID

**Response 200 OK**:
```json
{
  "id": "uuid-string",
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "user_id": "user-uuid-string",
  "created_at": "2026-01-14T10:00:00Z",
  "updated_at": "2026-01-14T10:00:00Z"
}
```

**Response 401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

**Response 403 Forbidden**:
```json
{
  "error": "Access denied - task does not belong to user"
}
```

**Response 404 Not Found**:
```json
{
  "error": "Task not found"
}
```

#### PUT /api/tasks/{id}
Update a specific task

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Path Parameters**:
- id: Task UUID

**Request**:
```json
{
  "title": "Updated task title",
  "description": "Updated task description",
  "completed": true
}
```

**Response 200 OK**:
```json
{
  "id": "uuid-string",
  "title": "Updated task title",
  "description": "Updated task description",
  "completed": true,
  "user_id": "user-uuid-string",
  "created_at": "2026-01-14T10:00:00Z",
  "updated_at": "2026-01-14T11:00:00Z"
}
```

**Response 400 Bad Request**:
```json
{
  "error": "Invalid input",
  "details": ["Title is required"]
}
```

**Response 401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

**Response 403 Forbidden**:
```json
{
  "error": "Access denied - task does not belong to user"
}
```

**Response 404 Not Found**:
```json
{
  "error": "Task not found"
}
```

#### DELETE /api/tasks/{id}
Delete a specific task

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Path Parameters**:
- id: Task UUID

**Response 204 No Content**

**Response 401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

**Response 403 Forbidden**:
```json
{
  "error": "Access denied - task does not belong to user"
}
```

**Response 404 Not Found**:
```json
{
  "error": "Task not found"
}
```

#### PATCH /api/tasks/{id}/complete
Toggle task completion status

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Path Parameters**:
- id: Task UUID

**Request**:
```json
{
  "completed": true
}
```

**Response 200 OK**:
```json
{
  "id": "uuid-string",
  "title": "Task title",
  "description": "Task description",
  "completed": true,
  "user_id": "user-uuid-string",
  "created_at": "2026-01-14T10:00:00Z",
  "updated_at": "2026-01-14T11:00:00Z"
}
```

**Response 400 Bad Request**:
```json
{
  "error": "Invalid input",
  "details": ["Completed field required"]
}
```

**Response 401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

**Response 403 Forbidden**:
```json
{
  "error": "Access denied - task does not belong to user"
}
```

**Response 404 Not Found**:
```json
{
  "error": "Task not found"
}
```