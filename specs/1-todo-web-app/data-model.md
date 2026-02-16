# Data Model: Phase II Todo Full-Stack Web Application

**Date**: 2026-01-14
**Feature**: 1-todo-web-app
**Input**: Feature spec and research findings

## Entities

### User
Represents a registered user in the system

**Fields**:
- id: UUID (Primary Key, auto-generated)
- email: String (Unique, Required, Validated)
- name: String (Optional)
- created_at: DateTime (Auto-generated, Immutable)
- updated_at: DateTime (Auto-generated, Updates on change)

**Validation Rules**:
- Email must be valid email format
- Email must be unique across all users
- Name length must be 1-100 characters if provided

### Task
Represents an individual task created by a user

**Fields**:
- id: UUID (Primary Key, auto-generated)
- title: String (Required, 1-200 characters)
- description: String (Optional, 0-1000 characters)
- completed: Boolean (Default: False)
- user_id: UUID (Foreign Key to User.id, Required)
- created_at: DateTime (Auto-generated, Immutable)
- updated_at: DateTime (Auto-generated, Updates on change)

**Validation Rules**:
- Title must be 1-200 characters
- Description must be 0-1000 characters if provided
- user_id must reference an existing user
- completed defaults to False

**Relationships**:
- Task.user_id → User.id (Many-to-One)

## Indexes

- User.email: Unique index for fast lookup and uniqueness enforcement
- Task.user_id: Index for efficient filtering by user
- Task.completed: Index for efficient filtering by completion status
- Task.created_at: Index for efficient ordering by creation date

## State Transitions

### Task Completion
- Initial state: completed = False
- Action: PATCH /api/tasks/{id}/complete with completed = true
- Result: completed = True
- Action: PATCH /api/tasks/{id}/complete with completed = false
- Result: completed = False

### Task Deletion
- Initial state: Task exists in database
- Action: DELETE /api/tasks/{id}
- Result: Task removed from database (hard delete)

## Constraints

- Referential integrity: Task.user_id must reference an existing User.id
- User isolation: All queries must filter by user_id to ensure data isolation
- Data validation: All fields validated at API and database level
- Timestamps: created_at immutable, updated_at automatically updated on changes