# Quick Start Guide: AI Todo Chatbot

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend integration)
- Access to Cohere API key
- Running Phase 2 backend services
- PostgreSQL database (Neon) with Phase 2 schema

## Setup

### 1. Environment Configuration
```bash
# Copy environment template
cp backend/.env.example backend/.env

# Add your Cohere API key
COHERE_API_KEY=your_cohere_api_key_here

# Ensure Phase 2 backend configuration is present
PHASE2_API_URL=https://mubashirjatoi-todo-ai-chatbot.hf.space
```

### 2. Install Dependencies
```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies (if extending UI)
cd frontend
npm install
```

### 3. Verify Phase 2 Integration
```bash
# Ensure Phase 2 APIs are accessible
curl https://mubashirjatoi-todo-ai-chatbot.hf.space/api/health

# Verify authentication is working
curl -H "Authorization: Bearer <valid-jwt-token>" https://mubashirjatoi-todo-ai-chatbot.hf.space/api/users/me
```

## Architecture Overview

### Agent Responsibilities
1. **ai-chatbot-orchestration-agent**: Coordinates the entire chatbot workflow
2. **nlp-intent-agent**: Processes natural language and identifies user intent
3. **task-ai-control-agent**: Maps intents to Phase 2 API calls
4. **user-context-agent**: Manages authentication and user session
5. **ai-backend-integration-agent**: Handles API communication with Phase 2
6. **ai-response-composer-agent**: Formats responses for user consumption
7. **ai-quality-guard-agent**: Validates requests and responses for safety

### Data Flow
```
User Input → NLP Intent Agent → User Context Agent → Task Control Agent →
Backend Integration Agent → Phase 2 API → Backend Integration Agent →
Response Composer Agent → Quality Guard Agent → User Output
```

## Running the Service

### Development Mode
```bash
# Start Phase 2 backend (if not already running)
cd backend && uvicorn main:app --reload

# Start chatbot service (in separate terminal)
cd backend && uvicorn ai_chatbot.main:app --reload
```

### Testing the Integration
```bash
# Test basic connectivity
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <valid-jwt-token>" \
  -d '{"message": "Add a task: Buy groceries"}'
```

## Key Components

### Intent Classification
- CREATE_TASK: "Add task: [title]", "Create [task name]"
- UPDATE_TASK: "Update [task] to [new title]", "Mark [task] as complete"
- DELETE_TASK: "Delete [task]", "Remove [task]"
- LIST_TASKS: "Show my tasks", "List all tasks"
- SEARCH_TASKS: "Find tasks with [keyword]", "Search [keyword]"
- FILTER_TASKS: "Show completed tasks", "Show incomplete tasks"
- SORT_TASKS: "Sort by [criteria]", "Order by [criteria]"
- GET_USER_INFO: "Who am I?", "What is my email?"

### Error Handling
- Authentication errors return 401 Unauthorized
- Authorization errors return 403 Forbidden
- Validation errors return 422 Unprocessable Entity
- AI processing errors return 500 Internal Server Error with user-friendly message

## Testing

### Unit Tests
```bash
# Run backend tests
cd backend && pytest tests/unit/

# Run integration tests
cd backend && pytest tests/integration/
```

### Contract Tests
- Verify all Phase 2 API calls work as expected
- Validate authentication token handling
- Test error scenarios and fallbacks