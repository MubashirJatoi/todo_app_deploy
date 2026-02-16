---
id: plan-001
title: Todo Web App Planning
stage: plan
date: 2026-01-14
author: Claude
---

# Todo Web App Planning

## Prompt

```
Phase II Implementation Architecture and Phases

## High-Level Architecture

System Components:
1. Frontend (Next.js) - User interface + JWT token management
2. Backend (FastAPI) - API endpoints + JWT verification
3. Database (Neon PostgreSQL) - Task and user data with indexes
4. Authentication (Better Auth) - Session + JWT token generation

Data Flow:
User Input → Frontend (Next.js) → API Client (attach JWT) → Backend (verify JWT + user_id) → Database (filtered by user_id) → Response → Frontend Display

## Implementation Phases

### Phase 2A: Database & Authentication
Create Neon database with users/tasks tables → Integrate Better Auth → Implement JWT validation middleware in FastAPI

Deliverables:
- ✓ Neon PostgreSQL database connected
- ✓ SQLModel User and Task models defined
- ✓ Better Auth configured on frontend
- ✓ FastAPI JWT verification middleware
- ✓ Environment variables setup

### Phase 2B: Backend API Implementation
Implement 6 REST endpoints with user isolation → Add error handling → Add request validation

Deliverables:
- ✓ GET /api/tasks (list user's tasks)
- ✓ POST /api/tasks (create new task)
- ✓ GET /api/tasks/{id} (get task details)
- ✓ PUT /api/tasks/{id} (update task)
- ✓ DELETE /api/tasks/{id} (delete task)
- ✓ PATCH /api/tasks/{id}/complete (toggle completion)
- ✓ All endpoints with user_id validation
- ✓ Error responses with proper status codes

### Phase 2C: Frontend Implementation
Build task pages and components → Implement API client → Add authentication flow

Deliverables:
- ✓ Login/Signup pages with Better Auth
- ✓ Task list page with responsive design
- ✓ Task creation form
- ✓ Task editing modal/page
- ✓ Task completion toggle
- ✓ Task deletion with confirmation
- ✓ Loading states and error handling
- ✓ JWT token handling in api.ts

### Phase 2D: Integration & Testing
Connect frontend to backend → Manual testing of all flows → Fix integration issues

Deliverables:
- ✓ End-to-end task creation working
- ✓ User isolation verified
- ✓ Responsive design tested
- ✓ Error handling tested
- ✓ Performance validated

## Testing Strategy

User Isolation Test:
1. Create User A account, create 5 tasks
2. Log out, create User B account, create 5 tasks
3. Verify User A sees only their 5 tasks (not B's)
4. Verify User B sees only their 5 tasks (not A's)

API Security Test:
1. Get valid JWT token
2. Try accessing /api/tasks with token → should work
3. Try accessing /api/tasks with invalid token → should get 401
4. Try accessing User B's tasks as User A → should get 403 or filter fails
5. Verify X-User-ID header can't be spoofed

Frontend Flow Test:
1. Cannot access task page without login → redirects to /auth/signin
2. Sign up → creates account and logs in automatically
3. Create task → appears in list immediately
4. Edit task → updates both UI and database
5. Complete task → toggles checkbox and persists
6. Delete task → shows confirmation, removes from list

Database Integrity Test:
1. Query tasks table directly → all have non-null user_id
2. Verify indexes exist on user_id and completed
3. Verify foreign key constraint works
4. Check created_at defaults to current timestamp

## Decisions Needing Documentation

| Decision | Option A | Option B | Choice | Rationale |
|----------|----------|----------|--------|-----------|
| JWT Expiry | 7 days | 24 hours | 7 days | Hackathon convenience, still secure |
| Task Limit | Unlimited | 100/user | Unlimited | No requirement to limit |
| Soft Delete | Yes (with deleted_at) | Hard delete only | Hard delete | Simpler for MVP |
| Default Sort | Created DESC | Title ASC | Created DESC | Most recent first = intuitive |
| Error Language | User-friendly | Technical | User-friendly | Better UX |
| CORS Policy | Allow all origins | Specific domain | localhost only | Development only |

## Quality Validation Checklist

Spec Compliance:
- [ ] All 5 basic features implemented
- [ ] All 6 API endpoints working
- [ ] Database schema matches specification
- [ ] Better Auth integration complete

Functionality:
- [ ] Create task: title (required), description (optional)
- [ ] View: list all user's tasks
- [ ] Update: change title/description
- [ ] Delete: remove task
- [ ] Complete: toggle status

Security:
- [ ] JWT token required for all API calls
- [ ] User ID validation on every query
- [ ] No SQL injection possible (SQLModel)
- [ ] CORS headers correct
- [ ] Passwords hashed (Better Auth handles)

Performance:
- [ ] API response time < 200ms (average)
- [ ] Database queries use indexes
- [ ] Frontend renders < 1s (Core Web Vitals)

Code Quality:
- [ ] No console.errors in production
- [ ] TypeScript strict mode enabled
- [ ] Python type hints on all functions
- [ ] No hardcoded secrets
- [ ] Follows monorepo CLAUDE.md guidelines

User Experience:
- [ ] Mobile responsive (375px+)
- [ ] Clear error messages
- [ ] Loading states visible
- [ ] Form validation before submit
- [ ] Confirmation on delete

## Technical Architecture Details

Frontend Structure:
/frontend
/app
/auth - login/signup pages
/tasks - task management pages
/layout.tsx - root layout with auth context
/components
TaskList.tsx
TaskForm.tsx
TaskCard.tsx
/lib
api.ts - API client with JWT handling
auth.ts - Better Auth setup

Backend Structure:
/backend
main.py - FastAPI app, middleware setup
models.py - SQLModel User and Task
db.py - Database connection
/routes
tasks.py - All task endpoints
auth.py - JWT validation helpers

Environment Setup:
- Frontend: .env.local with NEXT_PUBLIC_API_URL
- Backend: .env with DATABASE_URL, BETTER_AUTH_SECRET
- Database: Neon connection string
- Auth Secret: Same in frontend and backend
```

## Response

Created the implementation plan for the Phase II Todo Full-Stack Web Application with all required components. Generated research.md with technology decisions, data-model.md with entity definitions, API contracts for all endpoints, and a quickstart guide for development setup. The plan includes all phases and follows the constitutional requirements for spec-driven development, user isolation, security-first approach, and technology consistency.

```