import sys
import os
# Add the current directory to the Python path to resolve imports properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session
from fastapi.security import HTTPBearer

from db import create_db_and_tables, get_session
from routes import auth_routes as auth, tasks
from ai_chatbot.routes import chat_routes
from models import User, Task

# Import rate limiter
from ai_chatbot.services.rate_limiter import rate_limiter_service

# Import Dapr event handling utilities
import json
from typing import List, Dict, Any


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    create_db_and_tables()
    # Initialize rate limiter
    rate_limiter_service.init_app(app)
    yield


# Security scheme for Swagger UI
security_scheme = HTTPBearer()

# Create FastAPI app with lifespan
app = FastAPI(
    lifespan=lifespan,
    title="Todo API",
    version="1.0.0",
    redoc_url="/redoc",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Add CORS middleware for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fullstack-todo-hackathon-2-phase-2.vercel.app",  # Deployed frontend
        "https://frontend-xi-five-90.vercel.app",  # Previous deployed frontend
        "http://localhost:3000",  # Local frontend development
        "http://localhost:8000",  # Local backend for testing
        "https://mubashirjatoi-todo-ai-chatbot.hf.space",  # Deployed backend
        "http://127.0.0.1:3000",  # Alternative localhost for frontend
        "http://0.0.0.0:3000",    # Alternative localhost for frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(chat_routes.router, prefix="/api/chatbot", tags=["chatbot"])
# Include chat routes at /api/chat for frontend compatibility
from ai_chatbot.routes.chat_routes import router as chat_router
app.include_router(chat_router, prefix="/api", tags=["chat"])

# Handle both with and without trailing slash to avoid redirect issues for POST requests
from fastapi import Depends, HTTPException, status
import uuid
from routes import tasks as tasks_router_module
from auth import get_current_user_id
from db import get_session
from sqlmodel import Session

# Directly implement the endpoints without redirects to preserve POST data
@app.post("/api/tasks")
def create_task_no_redirect(task_data: tasks_router_module.TaskCreate, current_user_id: uuid.UUID = Depends(get_current_user_id), session: Session = Depends(get_session)):
    # Call the actual create_task function from the tasks router
    return tasks_router_module.create_task(task_data, current_user_id, session)

@app.get("/api/tasks")
def get_tasks_no_redirect(
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
    search: str = None,
    status: str = None,  # Changed from status_filter to match original
    priority: str = None,
    category: str = None,
    sort: str = None
):
    # Call the actual get_tasks function from the tasks router
    # We need to call it with the same parameters as the original function
    from routes.tasks import get_tasks
    return get_tasks(current_user_id=current_user_id, session=session, search=search, status=status, priority=priority, category=category, sort=sort)

# Dapr pub/sub event handling endpoints
@app.get("/dapr/subscribe")
def subscribe():
    """
    Dapr pub/sub subscription endpoint
    Returns a list of topics this service wants to subscribe to
    """
    subscriptions = [
        {
            "pubsubname": "pubsub",
            "topic": "task.created",
            "route": "/events/task-created"
        },
        {
            "pubsubname": "pubsub",
            "topic": "task.updated",
            "route": "/events/task-updated"
        },
        {
            "pubsubname": "pubsub",
            "topic": "task.deleted",
            "route": "/events/task-deleted"
        },
        {
            "pubsubname": "pubsub",
            "topic": "task.completed",
            "route": "/events/task-completed"
        }
    ]
    return subscriptions

@app.post("/events/task-created")
async def handle_task_created(data: Dict[Any, Any]):
    """
    Handle task.created events from Dapr pub/sub
    """
    print(f"Received task.created event: {data}")
    # Process the event - could log, trigger notifications, etc.
    # For now, just log the event
    event_data = data.get("data", {})
    task_id = event_data.get("task_id")
    user_id = event_data.get("user_id")
    title = event_data.get("title")
    
    print(f"Task created event processed - Task ID: {task_id}, User ID: {user_id}, Title: {title}")
    
    return {"status": "success"}

@app.post("/events/task-updated")
async def handle_task_updated(data: Dict[Any, Any]):
    """
    Handle task.updated events from Dapr pub/sub
    """
    print(f"Received task.updated event: {data}")
    # Process the event - could log, trigger notifications, etc.
    # For now, just log the event
    event_data = data.get("data", {})
    task_id = event_data.get("task_id")
    user_id = event_data.get("user_id")
    updated_fields = event_data.get("updated_fields", {})
    
    print(f"Task updated event processed - Task ID: {task_id}, User ID: {user_id}, Updated Fields: {updated_fields}")
    
    return {"status": "success"}

@app.post("/events/task-deleted")
async def handle_task_deleted(data: Dict[Any, Any]):
    """
    Handle task.deleted events from Dapr pub/sub
    """
    print(f"Received task.deleted event: {data}")
    # Process the event - could log, trigger notifications, etc.
    # For now, just log the event
    event_data = data.get("data", {})
    task_id = event_data.get("task_id")
    user_id = event_data.get("user_id")
    
    print(f"Task deleted event processed - Task ID: {task_id}, User ID: {user_id}")
    
    return {"status": "success"}

@app.post("/events/task-completed")
async def handle_task_completed(data: Dict[Any, Any]):
    """
    Handle task.completed events from Dapr pub/sub
    """
    print(f"Received task.completed event: {data}")
    # Process the event - could log, trigger notifications, etc.
    # For now, just log the event
    event_data = data.get("data", {})
    task_id = event_data.get("task_id")
    user_id = event_data.get("user_id")
    completed = event_data.get("completed")
    
    print(f"Task completed event processed - Task ID: {task_id}, User ID: {user_id}, Completed: {completed}")
    
    return {"status": "success"}

@app.get("/")
def read_root():
    return {"message": "Todo API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))  # Use port 8000 as default for standard API access
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)