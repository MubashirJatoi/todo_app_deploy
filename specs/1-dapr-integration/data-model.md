# Data Model: Dapr Infrastructure Integration

**Feature**: Dapr Infrastructure Integration (1-dapr-integration)
**Date**: 2026-02-08
**Phase**: 1 (Design & Contracts)

## Overview

This document defines the infrastructure-level entities and data structures for Dapr integration. These are NOT application data models (users, tasks, etc.) but rather Dapr-specific configurations and runtime structures.

---

## Entity 1: Dapr Sidecar Configuration

### Description
Represents the Dapr sidecar container injected into application pods via Kubernetes annotations.

### Attributes

| Attribute | Type | Description | Validation | Example |
|-----------|------|-------------|------------|---------|
| app-id | string | Unique identifier for Dapr application | Required, lowercase, hyphen-separated, max 63 chars | `backend-app` |
| app-port | integer | Port the application listens on | Required, 1-65535 | `8000` |
| log-level | enum | Dapr sidecar logging level | Optional, one of: debug\|info\|warn\|error | `info` |
| enable-metrics | boolean | Enable Prometheus metrics | Optional, default true | `true` |
| metrics-port | integer | Port for Prometheus metrics | Optional, default 9090 | `9090` |
| config | string | Reference to Dapr Configuration CRD | Optional | `appconfig` |

### Relationships
- **Injected Into**: Frontend Pod, Backend Pod (many-to-many)
- **References**: Dapr Components (via app-id scoping)
- **Exposes**: Metrics endpoint (if enabled)

### Validation Rules
1. `app-id` must match pattern `^[a-z0-9-]+$` (lowercase alphanumeric + hyphens)
2. `app-id` must match component scopes for access
3. `app-port` must match actual container port
4. `log-level` must be valid Dapr level

### Lifecycle
1. **Defined**: Via Helm values.yaml
2. **Injected**: By Dapr sidecar injector during pod creation
3. **Running**: Alongside application container
4. **Terminated**: When pod is deleted

### State Transitions
```
Configured → Pending → Running → Healthy | Unhealthy → Terminated
```

---

## Entity 2: Dapr Component (State Store)

### Description
Kubernetes Custom Resource defining a Dapr state store component backed by Redis.

### Attributes

| Attribute | Type | Description | Validation | Example |
|-----------|------|-------------|------------|---------|
| name | string | Component unique name | Required, DNS-1123 compliant | `statestore` |
| type | string | Component type identifier | Required, must be `state.redis` | `state.redis` |
| version | string | Component API version | Required | `v1` |
| namespace | string | Kubernetes namespace | Required | `default` |
| redisHost | string | Redis connection string | Required | `redis-master:6379` |
| redisPassword | secretRef | Kubernetes Secret reference | Required if auth enabled | `redis-secret.password` |
| enableTLS | boolean | Enable TLS connection | Optional, default false | `false` |
| scopes | array[string] | App-IDs that can access | Required | `["backend-app"]` |

### Relationships
- **Backed By**: Redis Instance (1-to-1)
- **Accessible By**: Backend App (many-to-many via scopes)
- **References**: Kubernetes Secret (for password)

### Validation Rules
1. `redisHost` must be reachable from pods
2. `redisPassword` secret must exist before component creation
3. `scopes` app-ids must exist (have running Dapr sidecars)
4. `type` must be supported Dapr state store type

### Lifecycle
1. **Created**: Via Helm install/upgrade
2. **Loaded**: By Dapr operator
3. **Active**: Available for state operations
4. **Deleted**: Via Helm uninstall or manual deletion

### State Transitions
```
Created → Loading → Ready | Error → Deleted
```

---

## Entity 3: Dapr Component (Pub/Sub)

### Description
Kubernetes Custom Resource defining a Dapr pub/sub component backed by Redis Streams.

### Attributes

| Attribute | Type | Description | Validation | Example |
|-----------|------|-------------|------------|---------|
| name | string | Component unique name | Required, DNS-1123 compliant | `pubsub` |
| type | string | Component type identifier | Required, must be `pubsub.redis` | `pubsub.redis` |
| version | string | Component API version | Required | `v1` |
| namespace | string | Kubernetes namespace | Required | `default` |
| redisHost | string | Redis connection string | Required | `redis-master:6379` |
| redisPassword | secretRef | Kubernetes Secret reference | Required if auth enabled | `redis-secret.password` |
| consumerID | string | Consumer group identifier | Required, unique per app | `todo-consumer` |
| redeliverInterval | duration | Redelivery wait time | Optional, default 30s | `30s` |
| maxRetries | integer | Max retry attempts | Optional, default 3 | `3` |
| scopes | array[string] | App-IDs that can access | Required | `["backend-app"]` |

### Relationships
- **Backed By**: Redis Instance (1-to-1, can share with state store)
- **Used By**: Backend App (publisher), Activity Service (subscriber)
- **References**: Kubernetes Secret (for password)

### Validation Rules
1. `consumerID` must be unique across all consumers
2. `redisHost` must be reachable
3. `redeliverInterval` must be positive duration
4. `maxRetries` must be non-negative integer

### Lifecycle
1. **Created**: Via Helm install/upgrade
2. **Loaded**: By Dapr operator
3. **Active**: Available for pub/sub operations
4. **Deleted**: Via Helm uninstall

### State Transitions
```
Created → Loading → Ready | Error → Deleted
```

---

## Entity 4: CloudEvent

### Description
Standardized event format (CloudEvents 1.0) for pub/sub messages.

### Attributes

| Attribute | Type | Description | Validation | Example |
|-----------|------|-------------|------------|---------|
| specversion | string | CloudEvents spec version | Required, must be "1.0" | `1.0` |
| type | string | Event type identifier | Required, pattern: `domain.entity.action` | `task.created` |
| source | string | Event source URI | Required | `/backend/tasks` |
| id | string | Unique event identifier | Required, UUID recommended | `550e8400-e29b-41d4-a716-446655440000` |
| time | string | Event timestamp | Optional, ISO 8601 format | `2026-02-08T12:00:00Z` |
| datacontenttype | string | MIME type of data | Optional, default `application/json` | `application/json` |
| data | object | Event payload | Required | `{"task_id": 123, "user_id": 456}` |

### Relationships
- **Published To**: Pub/Sub Component (many-to-1)
- **Delivered To**: Subscriber Endpoints (1-to-many)
- **Queued In**: Redis Streams (transient)

### Validation Rules
1. `specversion` must be exactly "1.0"
2. `type` must follow naming convention: `{domain}.{entity}.{action}`
3. `id` must be unique per event
4. `time` must be valid ISO 8601 timestamp if provided
5. `data` must be valid JSON if `datacontenttype` is `application/json`

### Lifecycle
1. **Created**: By publisher (backend application)
2. **Published**: To pub/sub topic
3. **Queued**: In Redis Streams
4. **Delivered**: To subscriber endpoints
5. **Acknowledged**: By subscriber (SUCCESS/RETRY/DROP)
6. **Expired**: After retention period or acknowledgment

### State Transitions
```
Created → Published → Queued → Delivered → Acknowledged | Retry | DLQ → Expired
```

### Event Types Defined

| Event Type | Source | Data Schema | Trigger |
|-----------|--------|-------------|---------|
| `task.created` | `/backend/tasks` | `{task_id, user_id, title, created_at}` | POST /tasks |
| `task.updated` | `/backend/tasks` | `{task_id, user_id, updated_fields}` | PUT /tasks/{id} |
| `task.deleted` | `/backend/tasks` | `{task_id, user_id, deleted_at}` | DELETE /tasks/{id} |
| `task.completed` | `/backend/tasks` | `{task_id, user_id, completed_at}` | PATCH /tasks/{id}/complete |

---

## Entity 5: State Store Entry

### Description
Key-value pair stored in Dapr state store (Redis) with optional TTL and metadata.

### Attributes

| Attribute | Type | Description | Validation | Example |
|-----------|------|-------------|------------|---------|
| key | string | Unique identifier | Required, recommend pattern: `domain:type:id` | `chat:session:123` |
| value | object | State data (any JSON) | Required | `{"messages": [...]}` |
| etag | string | Version tag for concurrency | Optional, auto-generated | `"v1"` |
| ttlInSeconds | integer | Time-to-live in seconds | Optional, positive integer | `3600` |
| consistency | enum | Consistency level | Optional, strong\|eventual | `eventual` |
| concurrency | enum | Concurrency control | Optional, first-write\|last-write | `last-write` |

### Relationships
- **Stored In**: State Store Component (many-to-1)
- **Accessed By**: Backend Application (via Dapr API)
- **Backed By**: Redis (physical storage)

### Validation Rules
1. `key` must be non-empty string (max 256 chars recommended)
2. `value` must be valid JSON
3. `ttlInSeconds` must be positive if provided
4. `consistency` must be valid Dapr consistency level
5. `concurrency` must be valid Dapr concurrency mode

### Lifecycle
1. **Saved**: Via Dapr state API (POST)
2. **Active**: Available for retrieval
3. **Expired**: After TTL elapses (if set)
4. **Deleted**: Via explicit DELETE or TTL expiration

### State Transitions
```
Saved → Active → Expired | Deleted
```

### Key Naming Convention

| Key Pattern | Description | TTL | Example |
|-------------|-------------|-----|---------|
| `chat:session:{user_id}` | Chat conversation history | 3600s (1 hour) | `chat:session:123` |
| `cache:user:{user_id}` | Cached user profile data | 1800s (30 min) | `cache:user:456` |
| `workflow:task:{workflow_id}` | Multi-step workflow state | 600s (10 min) | `workflow:task:789` |
| `cache:tasks:{user_id}` | Cached task list | 300s (5 min) | `cache:tasks:123` |

---

## Entity 6: Service Invocation Request

### Description
HTTP request routed through Dapr sidecar to target application identified by app-id.

### Attributes

| Attribute | Type | Description | Validation | Example |
|-----------|------|-------------|------------|---------|
| source_app_id | string | Calling application | Implicit from sidecar | `frontend-app` |
| target_app_id | string | Target application | Required in URL path | `backend-app` |
| method | string | HTTP method | Required, standard HTTP verbs | `GET` |
| path | string | Target endpoint path | Required, starts with `/` | `/tasks` |
| headers | object | HTTP headers | Optional, forwarded | `{"Authorization": "Bearer ..."}` |
| body | any | Request payload | Optional | `{"title": "New Task"}` |

### Relationships
- **Routed Through**: Dapr Sidecars (source + target)
- **Targets**: Application Endpoint (via app-id)
- **Returns**: HTTP Response (status, headers, body)

### Validation Rules
1. `target_app_id` must have running Dapr sidecar
2. `path` must be valid URI path
3. `method` must be valid HTTP verb
4. Target application must be listening on `app-port`

### Lifecycle
1. **Created**: By calling application
2. **Sent**: To local Dapr sidecar (localhost:3500)
3. **Routed**: To target Dapr sidecar (via app-id)
4. **Forwarded**: To target application container
5. **Response**: Returned through Dapr chain

### URL Format
```
http://localhost:3500/v1.0/invoke/{target_app_id}/method/{path}
```

**Example**:
```
http://localhost:3500/v1.0/invoke/backend-app/method/tasks
```

---

## Data Flow Diagrams

### Service Invocation Flow
```
Frontend Container (port 3000)
    ↓ HTTP Request to localhost:3500
Frontend Dapr Sidecar
    ↓ Service Discovery (backend-app)
    ↓ Network Call
Backend Dapr Sidecar
    ↓ HTTP Request to localhost:8000
Backend Container (port 8000)
    ↓ Process Request
    ↓ HTTP Response
Backend Dapr Sidecar
    ↓ Response Forwarded
Frontend Dapr Sidecar
    ↓ Response Returned
Frontend Container
```

### Pub/Sub Event Flow
```
Backend Container
    ↓ POST to localhost:3500/v1.0/publish/pubsub/task.created
Backend Dapr Sidecar
    ↓ Publish to Pub/Sub Component
Redis Streams
    ↓ Queue Message
    ↓ Deliver to Subscribers
Backend Dapr Sidecar (subscriber)
    ↓ POST to localhost:8000/events/task-created
Backend Container (event handler)
    ↓ Process Event
    ↓ Return SUCCESS/RETRY/DROP
Backend Dapr Sidecar
    ↓ Acknowledge or Retry
```

### State Management Flow
```
Backend Container
    ↓ POST to localhost:3500/v1.0/state/statestore
Backend Dapr Sidecar
    ↓ State Operation
State Store Component
    ↓ Redis Command
Redis Instance
    ↓ Store Key-Value
    ↓ Apply TTL (if set)
```

---

## Validation and Constraints

### Cross-Entity Validation

1. **App-ID Consistency**:
   - Sidecar `app-id` MUST match component `scopes`
   - Service invocation `target_app_id` MUST have running sidecar

2. **Port Consistency**:
   - Sidecar `app-port` MUST match container port
   - Dapr HTTP port always 3500 (non-configurable)

3. **Secret References**:
   - Component `redisPassword` secret MUST exist before component creation
   - Secret namespace MUST match component namespace

4. **Naming Conventions**:
   - App-IDs: `{service}-app` pattern
   - Topics: `{domain}.{entity}.{action}` pattern
   - State keys: `{domain}:{type}:{identifier}` pattern

### Infrastructure Constraints

1. **No Application Logic Changes**:
   - All entities are infrastructure-level
   - Application business logic remains unchanged
   - Only integration code added (Dapr SDK calls)

2. **Helm-Managed Lifecycle**:
   - All components created via Helm templates
   - No manual kubectl apply required
   - Single `helm install` deploys everything

3. **Backward Compatibility**:
   - Dapr can be disabled via `dapr.enabled=false`
   - Application functions without Dapr (direct HTTP)
   - No breaking changes to existing API contracts

---

## Summary

### Entities Defined: 6
1. Dapr Sidecar Configuration
2. Dapr Component (State Store)
3. Dapr Component (Pub/Sub)
4. CloudEvent
5. State Store Entry
6. Service Invocation Request

### Key Relationships
- Sidecars inject into Pods
- Components reference Secrets
- Components scope to App-IDs
- Events flow through Pub/Sub
- State entries stored in State Store
- Invocations route through Sidecars

### Validation Rules: 30+ rules defined across all entities

**Status**: ✅ Data Model Complete - Ready for Contract Generation
