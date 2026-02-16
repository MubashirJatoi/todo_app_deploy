---
id: constitution-001
title: Update Project Constitution to v1.0.0
stage: constitution
date: 2026-01-14
author: Claude
---

# Update Project Constitution to v1.0.0

## Prompt

```
Project: Phase II Todo Full-Stack Web Application
Description: Transform console todo app into modern multi-user web app with persistent storage, authentication, and REST API.

Core Principles:
- Spec-driven development: All implementation driven by specifications
- User isolation: Each user sees and modifies only their own tasks
- Security first: JWT authentication on all API endpoints
- Monorepo clarity: Single context for frontend and backend
- Technology consistency: Use prescribed stack (Next.js, FastAPI, SQLModel, Neon, Better Auth)

Key Standards:
- Specification compliance: Code must match spec requirements exactly
- API contract: All endpoints must match REST endpoint specification
- Database integrity: All queries must enforce user_id filtering
- Code organization: Follow CLAUDE.md guidelines in each folder
- Type safety: Use TypeScript in frontend, type hints in backend

Technology Stack (Non-Negotiable):
- Frontend: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- Backend: FastAPI, SQLModel, Pydantic
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth with JWT tokens
- ORM: SQLModel (no raw SQL)

Constraints:
- No manual database queries (use SQLModel only)
- No inline styles (Tailwind only)
- No server-side rendering exemptions without approval
- API responses must include user_id validation
- All environment variables must have defaults or explicit setup

Success Criteria:
- All 5 basic features implemented and working
- All REST endpoints functional with JWT authentication
- Frontend can create, read, update, delete, and complete tasks
- User isolation enforced (no data leakage between users)
- Database schema matches specification exactly
- Zero authentication bypass vulnerabilities
- Code passes linting and follows stack conventions

Acceptance Checklist:
- ✓ Task CRUD operations working end-to-end
- ✓ JWT authentication protecting all endpoints
- ✓ User isolation enforced on database level
- ✓ Frontend sends/receives data correctly
- ✓ Database schema created and indexed
- ✓ Better Auth integrated with FastAPI
- ✓ All features documented in specs
```

## Response

Updated the constitution file with the provided principles and standards for the Phase II Todo Full-Stack Web Application. Created a complete constitution document with Core Principles, Key Standards, Constraints, and Governance sections. Added a sync impact report and version tracking information.

```