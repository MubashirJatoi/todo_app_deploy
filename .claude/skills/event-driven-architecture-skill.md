# Event-Driven Architecture Skill

## Purpose
Design and implement event-driven patterns for loosely-coupled microservices communication.

## What it does
- Designs event schemas and naming conventions
- Defines event types for domain operations (created, updated, deleted)
- Plans event flow across microservices
- Implements choreography patterns (events trigger actions)
- Designs saga patterns for distributed transactions
- Ensures idempotent event handling
- Implements eventual consistency patterns

## What it does NOT do
- Implement Dapr components directly
- Write low-level pub/sub code
- Handle synchronous request-response patterns

## Usage
Use this skill when you need to:
- Convert tightly-coupled services to event-driven architecture
- Design event flows for complex business processes
- Plan event-driven refactoring of monolithic applications
- Implement eventual consistency across services

## Key Patterns
**Event Notification**: Publish events when state changes occur
**Event-Carried State Transfer**: Include full state in events to reduce queries
**Event Sourcing**: Store all state changes as sequence of events
**CQRS**: Separate read and write models with events

## Example Event Flow
```
User Action (Create Task via Chatbot)
  ↓
Chatbot Service: Publishes "task.create.requested" event
  ↓
Task Service: Subscribes, creates task, publishes "task.created" event
  ↓
Multiple Subscribers:
  - Activity Service: Logs action
  - Analytics Service: Updates metrics
  - Notification Service: Sends notification
  - Response Service: Sends confirmation to user
```
