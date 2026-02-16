#!/usr/bin/env python3
"""
Script to check if the application can connect to the Neon database
and verify if data exists in the tables.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path to resolve imports properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from db import engine, create_db_and_tables
from models import User, Task

def check_database_connection():
    """Test the database connection and check for existing data."""
    print("Checking database connection...")

    try:
        # Load environment variables
        load_dotenv()

        # Create tables if they don't exist
        create_db_and_tables()

        # Create a session to interact with the database
        with Session(engine) as session:
            print(f"Successfully connected to database: {engine.url}")

            # Count users
            user_count = session.exec(select(User)).all()
            print(f"Total users in database: {len(user_count)}")

            # Print user details if any exist
            for user in user_count:
                print(f"  - User ID: {user.id}, Email: {user.email}, Name: {user.name}")

            # Count tasks
            task_count = session.exec(select(Task)).all()
            print(f"Total tasks in database: {len(task_count)}")

            # Print task details if any exist
            for task in task_count:
                print(f"  - Task ID: {task.id}, Title: {task.title}, Completed: {task.completed}, User ID: {task.user_id}")

            # Show relationships - count tasks per user
            if user_count:
                print("\nTasks per user:")
                for user in user_count:
                    user_tasks = [task for task in task_count if task.user_id == user.id]
                    print(f"  - User {user.email}: {len(user_tasks)} tasks")

        print("\nDatabase check completed successfully!")
        return True

    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_database_connection()