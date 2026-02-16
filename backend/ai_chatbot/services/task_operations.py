"""
Task service module that provides functions for task operations.
This mirrors the functionality in routes/tasks.py but exposes it as services
that can be called from other parts of the application like the chatbot.
"""

from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from models import Task, User
from datetime import datetime, date
from services.task_service import (
    get_tasks_by_user,
    create_task_for_user,
    get_task_by_id_and_user,
    update_task_for_user,
    delete_task_for_user,
    toggle_task_completion
)


def get_user_tasks_service(
    session: Session,
    user_id: UUID,
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    sort: Optional[str] = None
) -> List[Task]:
    """
    Service function to get tasks for a specific user with optional filters.
    """
    # Get tasks for this user only using the service layer
    tasks = get_tasks_by_user(session, user_id)

    # Apply search filter if provided
    if search:
        search_lower = search.lower()
        tasks = [
            task for task in tasks
            if search_lower in task.title.lower() or
            (task.description and search_lower in task.description.lower()) or
            (task.category and search_lower in task.category.lower())
        ]

    # Apply status filter if provided
    if status == "pending":
        tasks = [task for task in tasks if not task.completed]
    elif status == "completed":
        tasks = [task for task in tasks if task.completed]

    # Apply priority filter if provided
    if priority:
        tasks = [task for task in tasks if task.priority == priority]

    # Apply category filter if provided
    if category:
        tasks = [task for task in tasks if task.category and category.lower() in task.category.lower()]

    # Apply sorting if provided
    if sort == "title":
        tasks.sort(key=lambda t: t.title.lower())
    elif sort == "priority":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        tasks.sort(key=lambda t: priority_order.get(t.priority, 3))
    elif sort == "due_date":
        tasks.sort(key=lambda t: (t.due_date is None, t.due_date))
    else:  # Default sort by created_at (most recent first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)

    return tasks


def create_task_service(
    session: Session,
    user_id: UUID,
    title: str,
    description: str = "",
    priority: str = "medium",
    category: Optional[str] = None,
    due_date: Optional[str] = None,
    recurrence_pattern: Optional[str] = None
) -> Task:
    """
    Service function to create a task for a specific user.
    """
    return create_task_for_user(
        session,
        user_id,
        title,
        description,
        priority,
        category,
        due_date,
        recurrence_pattern
    )


def update_task_service(
    session: Session,
    task_id: UUID,
    user_id: UUID,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    due_date: Optional[str] = None,
    recurrence_pattern: Optional[str] = None
) -> Optional[Task]:
    """
    Service function to update a task for a specific user.
    """
    return update_task_for_user(
        session,
        task_id,
        user_id,
        title=title,
        description=description,
        completed=completed,
        priority=priority,
        category=category,
        due_date=due_date,
        recurrence_pattern=recurrence_pattern
    )


def delete_task_service(
    session: Session,
    task_id: UUID,
    user_id: UUID
) -> bool:
    """
    Service function to delete a task for a specific user.
    """
    return delete_task_for_user(session, task_id, user_id)


def complete_task_service(
    session: Session,
    task_id: UUID,
    user_id: UUID,
    completed: bool
) -> Optional[Task]:
    """
    Service function to update task completion status for a specific user.
    """
    return toggle_task_completion(session, task_id, user_id, completed)