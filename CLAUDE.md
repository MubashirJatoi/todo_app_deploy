# Todo App - Phase II Hackathon

## Project Overview
Full-stack todo application with Next.js, FastAPI, Neon PostgreSQL.

## Spec-Kit Structure
- /specs/overview.md - Project overview
- /specs/features/ - Feature specifications
- /specs/api/ - REST API specs
- /specs/database/ - Database schema
- /specs/ui/ - UI component specs

## Development Workflow
1. Read spec: @specs/features/[feature].md
2. Implement: Use Claude Code with spec reference
3. Test and iterate

## Commands
- Frontend: cd frontend && npm run dev
- Backend: cd backend && uvicorn main:app --reload
- Both: docker-compose up