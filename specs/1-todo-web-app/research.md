# Research: Phase II Todo Full-Stack Web Application

**Date**: 2026-01-14
**Feature**: 1-todo-web-app
**Input**: Implementation plan from `/specs/1-todo-web-app/plan.md`

## Decision: Tech Stack Selection

**Rationale**: Selected Next.js 16+ with App Router for frontend due to its excellent developer experience, built-in optimizations, and strong TypeScript support. FastAPI was chosen for backend due to its automatic API documentation, type validation, and high performance. SQLModel for database ORM provides both SQLAlchemy power and Pydantic validation in one package.

**Alternatives considered**:
- React + Vite + Express: More complex setup, less type safety
- Remix: Great but more complex routing for this use case
- Django: Heavy for this simple API
- Prisma + Node.js: Good alternative but SQLModel fits better with Python ecosystem

## Decision: Authentication Approach

**Rationale**: Better Auth was selected as it provides a complete authentication solution with JWT support, social login capabilities, and excellent TypeScript support. It integrates seamlessly with Next.js and provides both client and server-side session management.

**Alternatives considered**:
- Next-Auth: Popular but less feature-rich than Better Auth
- Clerk: Good but introduces vendor lock-in
- Roll our own JWT: Time-consuming and error-prone
- Firebase Auth: Overkill for this simple use case

## Decision: Database and Hosting

**Rationale**: Neon PostgreSQL was chosen for its serverless capabilities, instant branching features, and seamless integration with SQLModel. The serverless nature provides cost efficiency during development while scaling appropriately.

**Alternatives considered**:
- SQLite: Simpler but lacks advanced features needed for production
- PostgreSQL on VM: More complex setup and management
- Supabase: Similar to Neon but with more vendor-specific features
- MongoDB: Good for flexibility but SQL is better for relational data

## Decision: API Design Pattern

**Rationale**: RESTful API design was chosen for its simplicity, wide tooling support, and familiarity to most developers. The standard CRUD operations map cleanly to HTTP methods with clear resource paths.

**Alternatives considered**:
- GraphQL: More flexible but adds complexity for this simple use case
- RPC-style: Less standardized approach
- gRPC: Excellent performance but overkill for web frontend

## Decision: Frontend State Management

**Rationale**: Minimal state management needed since most state is stored on the backend. React's built-in useState and useContext hooks are sufficient, with Better Auth handling session state.

**Alternatives considered**:
- Redux: Overkill for this simple application
- Zustand: Good for medium complexity but unnecessary here
- Jotai: Interesting approach but not needed for this scope

## Decision: Styling Approach

**Rationale**: Tailwind CSS was chosen for its utility-first approach, which speeds up development and ensures consistent styling without creating numerous custom CSS classes.

**Alternatives considered**:
- Styled-components: Good but increases bundle size
- CSS Modules: More traditional but requires more custom class management
- Vanilla CSS: Possible but less maintainable

## Decision: Task Completion Toggle Method

**Rationale**: Using a PATCH request to /api/tasks/{id}/complete endpoint was chosen as it's semantically appropriate for partial updates and follows REST conventions well.

**Alternatives considered**:
- PUT request: Would require sending full task object
- Separate endpoint: Less RESTful
- Boolean field in PUT: Would mix update operations