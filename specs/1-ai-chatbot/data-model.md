# Data Model: AI Todo Chatbot

## Core Entities

### Natural Language Command
- **Purpose**: Represents user input in plain language that must be parsed into specific actions
- **Fields**:
  - text_content: string (the raw user input)
  - timestamp: datetime (when the command was received)
  - user_context: object (authenticated user information)
- **Relationships**: Belongs to authenticated user
- **Validation**: Must be non-empty, must come from authenticated user

### User Context
- **Purpose**: Represents the authenticated user's identity and session state required for all operations
- **Fields**:
  - user_id: string (unique identifier from Phase 2)
  - email: string (user's email address)
  - authentication_token: string (valid JWT token)
  - session_data: object (temporary conversation state)
- **Relationships**: Links to Phase 2 user record
- **Validation**: Token must be valid and unexpired

### Task Reference
- **Purpose**: Represents identifiers that point to specific tasks, either explicit (by title) or contextual ("that one", "first task")
- **Fields**:
  - reference_type: enum (explicit, contextual, positional)
  - identifier: string (title, description, or contextual reference)
  - resolved_task_id: string (Phase 2 task ID when resolved)
  - ambiguity_score: float (confidence in reference resolution)
- **Relationships**: Points to Phase 2 task
- **Validation**: Must resolve to an existing task for the authenticated user

### Intent
- **Purpose**: Represents the specific action the user wants to perform (create, update, delete, search, etc.)
- **Fields**:
  - intent_type: enum (CREATE_TASK, UPDATE_TASK, DELETE_TASK, LIST_TASKS, SEARCH_TASKS, FILTER_TASKS, SORT_TASKS, GET_USER_INFO)
  - confidence_score: float (AI confidence in intent classification)
  - parameters: object (extracted entities for the intent)
  - extracted_entities: array (entities extracted from the command)
- **Relationships**: May relate to one or more Task References
- **Validation**: Must map to a valid Phase 2 operation

## State Transitions

### Conversation State
- **START**: Initial state when user begins interaction
- **PROCESSING**: When intent is being determined
- **AWAITING_CLARIFICATION**: When ambiguous reference requires user input
- **CONFIRMATION_REQUIRED**: When destructive action needs confirmation
- **EXECUTING**: When Phase 2 API call is in progress
- **RESPONSE_READY**: When response is prepared for user
- **END**: Final state after response delivery

## Validation Rules

### From Requirements
- All commands must be authenticated before processing
- User data isolation must be maintained (can only access user's own tasks)
- Destructive actions must be confirmed before execution
- Natural language must be parsed into valid intents
- Task references must resolve to valid Phase 2 tasks

### Business Logic Constraints
- Cannot bypass Phase 2 authentication
- Cannot bypass Phase 2 business rules
- Cannot access other users' data
- Must preserve existing Phase 2 behavior