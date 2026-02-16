# REST API Endpoints

## Authentication
All endpoints require JWT token: Authorization: Bearer <token>

## Endpoints

### GET /api/tasks
List all tasks for authenticated user.

### POST /api/tasks
Create a new task. Body: { title, description }

### GET /api/tasks/{id}
Get task details.

### PUT /api/tasks/{id}
Update task.

### DELETE /api/tasks/{id}
Delete task.

### PATCH /api/tasks/{id}/complete
Toggle task completion.