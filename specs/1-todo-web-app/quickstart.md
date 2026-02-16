# Quickstart Guide: Phase II Todo Full-Stack Web Application

**Date**: 2026-01-14
**Feature**: 1-todo-web-app
**Purpose**: Get the application running locally for development

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- PostgreSQL-compatible database (Neon recommended)
- Git

## Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd hackathon-todo
```

2. Set up backend:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up frontend:
```bash
cd frontend
npm install
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL="postgresql://username:password@localhost:5432/todo_app"
BETTER_AUTH_SECRET="your-super-secret-jwt-key-here-make-it-long-and-random"
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL="https://mubashirjatoi-todo-ai-chatbot.hf.space"
NEXTAUTH_URL="http://localhost:3000"
```

## Database Setup

1. Install Neon CLI or connect to your PostgreSQL instance
2. Create a new database for the application
3. Update DATABASE_URL in backend/.env with your connection string

## Running the Application

### Development Mode

1. Start the backend:
```bash
cd backend
uvicorn main:app --reload
```
Backend will be available at https://mubashirjatoi-todo-ai-chatbot.hf.space

2. Start the frontend:
```bash
cd frontend
npm run dev
```
Frontend will be available at http://localhost:3000

### Using Docker Compose (Alternative)

```bash
docker-compose up
```

## API Testing

Once running, you can test the API endpoints:

1. Register a user:
```bash
curl -X POST https://mubashirjatoi-todo-ai-chatbot.hf.space/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "name": "Test User"}'
```

2. Create a task:
```bash
# First, authenticate to get a token
curl -X POST https://mubashirjatoi-todo-ai-chatbot.hf.space/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Then use the token to create a task
curl -X POST https://mubashirjatoi-todo-ai-chatbot.hf.space/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title": "Sample Task", "description": "Sample Description"}'
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Verify DATABASE_URL is correct and database is accessible
2. **Authentication Fails**: Ensure BETTER_AUTH_SECRET is the same in frontend and backend
3. **CORS Errors**: Check that frontend and backend ports match your configuration
4. **Migration Issues**: Run database migrations if required by the application

### Resetting the Database

If you need to reset the database for testing:
```bash
# This would typically run a script to drop and recreate tables
python backend/scripts/reset_db.py
```