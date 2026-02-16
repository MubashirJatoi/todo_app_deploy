# Microservice Boundary Analysis Skill

## Purpose
Analyze and define clear service boundaries for microservice decomposition based on domain-driven design.

## What it does
- Analyzes monolithic application structure
- Identifies bounded contexts and aggregates
- Defines service responsibilities and ownership
- Maps data dependencies between services
- Identifies shared vs. service-specific concerns
- Documents service communication patterns
- Plans data migration and consistency strategies

## What it does NOT do
- Implement the actual service code
- Deploy or configure services
- Write Dapr components

## Usage
Use this skill when you need to:
- Decompose a monolith into microservices
- Define what each service should own
- Identify which operations should be synchronous vs. asynchronous
- Plan service communication and dependencies
- Determine database-per-service boundaries

## Analysis Criteria
**Cohesion**: Related functionality should be in the same service
**Coupling**: Minimize dependencies between services
**Data Ownership**: Each service owns its own data
**Autonomy**: Services can be developed and deployed independently
**Business Capability**: Services align with business domains

## Example Analysis
```
Current Monolith:
- Auth logic
- Task CRUD
- Chatbot NLP
- Activity logging

Proposed Services:
1. Auth Service (owns users)
2. Task Service (owns tasks)
3. Chatbot Service (owns chat history, NLP)
4. Activity Service (owns activity logs)

Communication:
- Chatbot → Task: Async (pub/sub) for task operations
- Frontend → Task: Sync (service invocation) for UI
- All → Activity: Async (pub/sub) for logging
```
