# Backend Guidelines

## Stack
- FastAPI (Python 3.9+)
- SQLModel ORM
- Neon PostgreSQL

## Project Structure
- main.py - FastAPI app
- models.py - SQLModel database models
- routes/ - API route handlers
- db.py - Database connection

## API Conventions
- All routes under /api/
- Return JSON responses
- Use Pydantic models
- Handle errors with HTTPException

## Running
uvicorn main:app --reload --port 8000