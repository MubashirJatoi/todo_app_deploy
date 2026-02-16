# Feature Specification: Dapr Infrastructure Integration

**Feature Branch**: `1-dapr-integration`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Phase V Dapr Integration: Transform Kubernetes-deployed system into distributed microservices architecture using Dapr sidecars, components, service invocation, pub/sub, and state management"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - DevOps Engineer Deploys Dapr-Enabled System (Priority: P1)

As a DevOps engineer, I need to deploy the entire todo application with Dapr capabilities enabled so that the system runs as a distributed microservices architecture without changing application code.

**Why this priority**: This is the foundation—without Dapr sidecars running, no other distributed capabilities are possible. This validates the infrastructure transformation.

**Independent Test**: Can be fully tested by running `helm install todo-app ./helm/todo-chart` and verifying each pod shows 2/2 containers (app + daprd sidecar) using `kubectl get pods` and `dapr list -k` shows all services.

**Acceptance Scenarios**:

1. **Given** existing Helm chart is installed, **When** I run `helm upgrade todo-app ./helm/todo-chart` with Dapr enabled, **Then** each pod (frontend, backend) deploys with 2 containers
2. **Given** Dapr-enabled pods are running, **When** I execute `dapr list -k`, **Then** output shows frontend-app on port 3000 and backend-app on port 8000
3. **Given** Dapr sidecars are injected, **When** I check pod logs using `kubectl logs <pod-name> -c daprd`, **Then** logs show "dapr initialized. Status: Running"

---

### User Story 2 - System Architect Establishes Distributed Communication (Priority: P1)

As a system architect, I need services to communicate through Dapr service invocation instead of direct HTTP calls so that the system gains built-in resilience, service discovery, and distributed tracing.

**Why this priority**: Service invocation is the core pattern for synchronous communication in distributed systems. Without this, services remain tightly coupled with hardcoded URLs.

**Independent Test**: Can be fully tested by calling frontend API which invokes backend via Dapr, and verifying through Dapr logs that invocation occurred (no direct HTTP call between pods).

**Acceptance Scenarios**:

1. **Given** frontend needs to fetch tasks, **When** frontend calls Dapr sidecar at `localhost:3500/v1.0/invoke/backend-app/method/tasks`, **Then** request routes through Dapr to backend service
2. **Given** backend service is invoked via Dapr, **When** I check Dapr sidecar logs, **Then** logs show "invoking target backend-app, method: /tasks"
3. **Given** services communicate via Dapr, **When** backend service is temporarily unavailable, **Then** Dapr retry policy automatically retries the request

---

### User Story 3 - Platform Engineer Enables Event-Driven Operations (Priority: P2)

As a platform engineer, I need task operations (create, update, delete) to publish events to pub/sub topics so that multiple services can react to task changes asynchronously without tight coupling.

**Why this priority**: Event-driven architecture enables loose coupling and allows multiple consumers (activity logging, analytics, notifications) to react to task events independently.

**Independent Test**: Can be fully tested by creating a task via API, verifying event is published to `task.created` topic, and confirming subscriber receives the event via logs.

**Acceptance Scenarios**:

1. **Given** a new task is created via backend API, **When** task creation completes, **Then** backend publishes `task.created` event to pub/sub component
2. **Given** activity service subscribes to `task.*` events, **When** `task.created` event is published, **Then** activity service receives event and logs activity record
3. **Given** multiple subscribers listen to same topic, **When** event is published, **Then** all subscribers receive the event independently

---

### User Story 4 - Backend Developer Implements Distributed State Management (Priority: P3)

As a backend developer, I need to store chat session history and temporary state in Dapr state store so that the system benefits from distributed caching and reduces database load for ephemeral data.

**Why this priority**: State management optimizes performance by caching frequently accessed data and storing temporary workflow state, but core functionality works without it.

**Independent Test**: Can be fully tested by initiating a chatbot conversation, storing session state via Dapr HTTP API, retrieving it later, and verifying TTL expiration after configured time.

**Acceptance Scenarios**:

1. **Given** chatbot processes user message, **When** session state is saved via `POST localhost:3500/v1.0/state/statestore`, **Then** state persists in Redis with configured TTL
2. **Given** session state exists in state store, **When** retrieved via `GET localhost:3500/v1.0/state/statestore/{key}`, **Then** returns stored session data
3. **Given** state is saved with 1-hour TTL, **When** 1 hour elapses, **Then** state automatically expires and returns null

---

### User Story 5 - SRE Monitors Distributed System Health (Priority: P3)

As an SRE, I need to verify Dapr sidecar status, inspect component health, and view distributed traces so that I can ensure the distributed system operates correctly and troubleshoot issues quickly.

**Why this priority**: Observability is critical for production systems but can be added after core functionality is proven. Essential for long-term operations.

**Independent Test**: Can be fully tested by running `dapr list -k`, checking component status via `kubectl get components`, and verifying traces appear in Zipkin UI.

**Acceptance Scenarios**:

1. **Given** system is deployed, **When** I run `dapr list -k`, **Then** output shows all app-ids with correct ports and healthy status
2. **Given** Dapr components are deployed, **When** I run `kubectl get components -n default`, **Then** statestore and pubsub components show CREATED status
3. **Given** distributed tracing is enabled, **When** I make a request through frontend to backend, **Then** trace appears in Zipkin showing complete request path with timing

---

### Edge Cases

- What happens when Redis state store becomes temporarily unavailable?
  - Dapr should return error responses and application must handle gracefully
  - Service invocation continues to work (independent of state store)
- How does system handle pub/sub message delivery failures?
  - Dapr retries based on configured retry policy (default 3 times with exponential backoff)
  - Failed messages route to dead letter queue after max retries
- What if a service subscribes to events but is not running?
  - Messages queue in Redis Streams until subscriber becomes available
  - Dapr redelivers messages when subscriber comes back online
- How does system behave if Dapr sidecar crashes?
  - Pod shows 1/2 containers (only app container running)
  - Service becomes unreachable via Dapr invocation until sidecar restarts
  - Kubernetes automatically restarts daprd container

## Requirements *(mandatory)*

### Functional Requirements

#### 1. Dapr Sidecar Enablement

- **FR-001**: Frontend deployment MUST include Dapr sidecar with app-id "frontend-app" and app-port "3000"
- **FR-002**: Backend deployment MUST include Dapr sidecar with app-id "backend-app" and app-port "8000"
- **FR-003**: Dapr sidecars MUST be enabled via pod annotations in deployment templates
- **FR-004**: Dapr sidecars MUST expose metrics on port 9090
- **FR-005**: Dapr log level MUST be configurable via Helm values (default: "info")

#### 2. Dapr Components

- **FR-006**: System MUST include a Redis-based state store component named "statestore"
- **FR-007**: State store component MUST be deployed to "default" namespace
- **FR-008**: State store component MUST use Kubernetes Secret for Redis password authentication
- **FR-009**: State store component MUST scope access to backend-app only
- **FR-010**: System MUST include a Redis-based pub/sub component named "pubsub"
- **FR-011**: Pub/sub component MUST use Redis Streams as message broker
- **FR-012**: Pub/sub component MUST scope access to backend-app
- **FR-013**: Dapr components MUST be deployed as Kubernetes resources via Helm templates

#### 3. Service Invocation

- **FR-014**: Frontend MUST call backend API using Dapr invocation URL format: `http://localhost:3500/v1.0/invoke/backend-app/method/{endpoint}`
- **FR-015**: Service invocation MUST NOT use direct pod-to-pod HTTP calls or hardcoded service URLs
- **FR-016**: Dapr service invocation MUST use default HTTP port 3500 for sidecar communication
- **FR-017**: Service invocation MUST propagate HTTP headers (authorization, correlation-id) through Dapr

#### 4. Pub/Sub Events

- **FR-018**: Backend MUST publish "task.created" event when new task is created
- **FR-019**: Backend MUST publish "task.updated" event when task is modified
- **FR-020**: Backend MUST publish "task.deleted" event when task is removed
- **FR-021**: Backend MUST publish "task.completed" event when task is marked done
- **FR-022**: Events MUST follow topic naming convention: `<domain>.<entity>.<action>` (e.g., "task.created")
- **FR-023**: Activity service MUST subscribe to all "task.*" events for logging
- **FR-024**: Event payloads MUST include: event-id, timestamp, user-id, entity-id, and event-specific data
- **FR-025**: Event subscription configuration MUST be exposed via `/dapr/subscribe` endpoint

#### 5. State Management

- **FR-026**: Chat session history MUST be stored in Dapr state store with key format: `chat:session:{user_id}`
- **FR-027**: Chat session state MUST include TTL metadata set to 3600 seconds (1 hour)
- **FR-028**: User session cache MUST be stored in state store with key format: `cache:user:{user_id}`
- **FR-029**: State operations MUST use Dapr HTTP API: `POST/GET/DELETE /v1.0/state/{storename}`
- **FR-030**: Temporary workflow state MUST be stored with 600 seconds (10 minutes) TTL

#### 6. Helm Chart Integration

- **FR-031**: Dapr annotations MUST be conditionally added to deployment templates based on `dapr.enabled` flag in values.yaml
- **FR-032**: Dapr component YAMLs MUST be placed in `helm/todo-chart/templates/dapr-components/` directory
- **FR-033**: values.yaml MUST include section for Dapr configuration (enabled flag, log level, app-ids, ports)
- **FR-034**: Helm chart MUST support enabling/disabling Dapr via single flag without code changes
- **FR-035**: Redis connection strings for Dapr components MUST reference Kubernetes Secrets

#### 7. Observability

- **FR-036**: System MUST support verification via `dapr list -k` command showing all app-ids
- **FR-037**: Dapr sidecar logs MUST be accessible via `kubectl logs <pod-name> -c daprd`
- **FR-038**: Pod verification MUST show 2/2 containers (app + daprd) for each service
- **FR-039**: Distributed tracing MUST be configurable via Dapr Configuration resource
- **FR-040**: Dapr components status MUST be verifiable via `kubectl get components`

#### 8. Networking & Ports

- **FR-041**: Dapr HTTP port MUST be 3500 (default, non-configurable in this phase)
- **FR-042**: Dapr gRPC port MUST be 50001 (default, non-configurable in this phase)
- **FR-043**: Frontend container MUST communicate with its local Dapr sidecar at localhost:3500
- **FR-044**: Backend container MUST communicate with its local Dapr sidecar at localhost:3500
- **FR-045**: Inter-service communication MUST flow through Dapr sidecars, not direct pod IPs

#### 9. Distributed Architecture Blueprint

- **FR-046**: Helm chart structure MUST be reusable for similar multi-tier applications
- **FR-047**: Dapr component templates MUST use generic naming allowing easy customization
- **FR-048**: Folder structure MUST separate Dapr-specific templates from application templates
- **FR-049**: values.yaml Dapr section MUST be self-documenting with clear comments

#### 10. Constraints

- **FR-050**: NO changes to application business logic are permitted
- **FR-051**: NO changes to API contracts or endpoints are permitted
- **FR-052**: NO changes to database schemas are permitted
- **FR-053**: System MUST remain fully functional via `helm install` command
- **FR-054**: All Dapr configuration MUST be externalized to Helm values (no hardcoded settings)

### Key Entities *(include if feature involves data)*

- **Dapr Sidecar**: Container injected alongside application container providing distributed capabilities via localhost API
  - Attributes: app-id, app-port, log-level, metrics-port
  - Lifecycle: Managed by Kubernetes, injected via annotations

- **Dapr Component**: Kubernetes custom resource defining building blocks (state store, pub/sub)
  - Attributes: name, type, version, metadata, scopes
  - Types: state.redis, pubsub.redis

- **State Store Entry**: Key-value data stored in Redis via Dapr state API
  - Attributes: key, value, metadata (TTL, consistency, concurrency)
  - Key format: `{domain}:{type}:{identifier}` (e.g., `chat:session:123`)

- **Pub/Sub Event**: CloudEvents-formatted message published to topic
  - Attributes: specversion, type, source, id, time, datacontenttype, data
  - Topic format: `{domain}.{entity}.{action}` (e.g., `task.created`)

- **Service Invocation Request**: HTTP request routed through Dapr sidecar to target service
  - Attributes: app-id (target), method (endpoint path), headers, body
  - URL format: `http://localhost:3500/v1.0/invoke/{app-id}/method/{path}`

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Each pod shows 2/2 containers in `kubectl get pods` output (app + daprd sidecar)
- **SC-002**: `dapr list -k` command returns all services with correct app-ids and ports within 5 seconds
- **SC-003**: Frontend-to-backend API calls complete through Dapr invocation with latency increase of less than 50ms compared to direct calls
- **SC-004**: Task creation event flows through pub/sub and is received by activity subscriber within 1 second
- **SC-005**: Chat session state persists in Dapr state store and expires correctly after configured TTL
- **SC-006**: System deploys successfully via single `helm install` command without manual intervention
- **SC-007**: All Dapr components (statestore, pubsub) show "CREATED" status in `kubectl get components` output
- **SC-008**: Distributed traces appear in tracing backend (if configured) showing complete request path across services
- **SC-009**: System handles 1000 concurrent requests with Dapr enabled without degradation
- **SC-010**: Application functionality remains 100% identical to pre-Dapr behavior (no regressions)

## Assumptions *(document reasonable defaults)*

- **Assumption 1**: Dapr runtime is pre-installed on Kubernetes cluster via `dapr init -k` before Helm deployment
- **Assumption 2**: Redis is available in-cluster or external Redis endpoint is provided via Helm values
- **Assumption 3**: Kubernetes cluster supports sidecar injection and has sufficient resources for additional containers
- **Assumption 4**: Default Dapr HTTP port 3500 and gRPC port 50001 do not conflict with application ports
- **Assumption 5**: Namespace "default" is used for all deployments unless overridden in Helm values
- **Assumption 6**: mTLS between Dapr sidecars is disabled initially (can be enabled later via Configuration)
- **Assumption 7**: Distributed tracing backend (Zipkin/Jaeger) is optional and configured separately
- **Assumption 8**: Application code can be modified to add Dapr SDK calls without changing business logic
- **Assumption 9**: Redis authentication credentials are provided via Kubernetes Secrets before deployment
- **Assumption 10**: Helm chart version remains backward compatible (can deploy without Dapr if flag disabled)

## Dependencies *(list external requirements)*

- **Dependency 1**: Dapr CLI and runtime must be installed on Kubernetes cluster (version 1.10+)
- **Dependency 2**: Redis instance (in-cluster or external) accessible from Kubernetes pods
- **Dependency 3**: Kubernetes Secrets must exist for Redis password before Helm install
- **Dependency 4**: Kubernetes cluster must support CustomResourceDefinitions (for Dapr components)
- **Dependency 5**: kubectl access with permissions to create components, deployments, services

## Out of Scope *(explicitly exclude)*

- **OOS-001**: Application code refactoring or business logic changes
- **OOS-002**: Database schema modifications or migration scripts
- **OOS-003**: New application features or UI enhancements
- **OOS-004**: Production-grade observability stack deployment (Prometheus, Grafana, Zipkin)
- **OOS-005**: Dapr mTLS configuration and certificate management
- **OOS-006**: Multi-namespace or multi-cluster Dapr configuration
- **OOS-007**: Dapr actor framework implementation
- **OOS-008**: Dapr bindings or output bindings integration
- **OOS-009**: Dapr secrets management building block
- **OOS-010**: Performance optimization and load testing at scale
- **OOS-011**: Disaster recovery and backup procedures for Dapr state
- **OOS-012**: Automated rollback strategies for failed Dapr deployments

## Technical Specifications *(infrastructure-focused)*

### 1. Dapr Sidecar Enablement Specification

**Pods Requiring Dapr Annotations**:
- Frontend deployment (`helm/todo-chart/templates/frontend/deployment.yaml`)
- Backend deployment (`helm/todo-chart/templates/backend/deployment.yaml`)

**Required Annotation Keys and Values**:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "<service-app-id>"
  dapr.io/app-port: "<service-port>"
  dapr.io/log-level: "info"
  dapr.io/enable-metrics: "true"
  dapr.io/metrics-port: "9090"
```

**App ID and Port Strategy**:
- Frontend: app-id="frontend-app", app-port="3000"
- Backend: app-id="backend-app", app-port="8000"
- Naming convention: `{service-name}-app` (lowercase, hyphen-separated)

---

### 2. Dapr Components Specification

#### a) State Store Component

**File Location**: `helm/todo-chart/templates/dapr-components/statestore.yaml`

**YAML Structure**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: {{ .Release.Namespace }}
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: {{ .Values.dapr.stateStore.redisHost | quote }}
  - name: redisPassword
    secretKeyRef:
      name: {{ .Values.dapr.stateStore.secretName }}
      key: {{ .Values.dapr.stateStore.secretKey }}
  - name: enableTLS
    value: "false"
  scopes:
  - backend-app
```

**Namespace Placement**: Same namespace as Helm release (default: "default")

**Naming Conventions**:
- Component name: "statestore" (fixed)
- Secret reference: Configurable via values.yaml
- Scopes: List of app-ids that can access this component

#### b) Pub/Sub Component

**File Location**: `helm/todo-chart/templates/dapr-components/pubsub.yaml`

**YAML Structure**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: {{ .Release.Namespace }}
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: {{ .Values.dapr.pubsub.redisHost | quote }}
  - name: redisPassword
    secretKeyRef:
      name: {{ .Values.dapr.pubsub.secretName }}
      key: {{ .Values.dapr.pubsub.secretKey }}
  - name: consumerID
    value: "{{ .Release.Name }}-consumer"
  scopes:
  - backend-app
```

**Topic Naming Conventions**:
- Format: `{domain}.{entity}.{action}`
- Examples: `task.created`, `task.updated`, `task.deleted`, `task.completed`
- Domain: "task" (singular, lowercase)
- Actions: past-tense verbs (created, updated, deleted, completed)

---

### 3. Service Invocation Specification

**Frontend to Backend Invocation**:

**Current (Direct)**:
```
http://backend-service:8000/tasks
```

**New (Dapr Invocation)**:
```
http://localhost:3500/v1.0/invoke/backend-app/method/tasks
```

**Invocation URL Structure**:
- Base: `http://localhost:{dapr-http-port}`
- Path: `/v1.0/invoke/{target-app-id}/method/{endpoint-path}`
- Example: `http://localhost:3500/v1.0/invoke/backend-app/method/auth/login`

**Replacement Strategy**:
- Frontend code must replace environment variable `NEXT_PUBLIC_API_BASE_URL`
- Old value: `http://backend-service:8000` or `http://localhost:8000`
- New value: `http://localhost:3500/v1.0/invoke/backend-app/method`
- NO changes to endpoint paths themselves (e.g., `/tasks` remains `/tasks`)

---

### 4. Pub/Sub Event Specification

**Operations Publishing Events**:

| Operation | Topic | Publisher | Payload |
|-----------|-------|-----------|---------|
| Create Task | task.created | backend-app | `{task_id, user_id, title, created_at}` |
| Update Task | task.updated | backend-app | `{task_id, user_id, updated_fields}` |
| Delete Task | task.deleted | backend-app | `{task_id, user_id, deleted_at}` |
| Complete Task | task.completed | backend-app | `{task_id, user_id, completed_at}` |

**Topic Naming Strategy**:
- Pattern: `{domain}.{entity}.{action}`
- Domain: Fixed to "task" for this feature
- Entity: Always singular (task, not tasks)
- Action: Past-tense verb (created, updated, deleted, completed)

**Subscription Matrix**:

| Service | Subscribed Topics | Purpose |
|---------|------------------|---------|
| backend-app | N/A (publisher only) | Publishes all task events |
| activity-service | task.* (wildcard) | Logs all task activities |

**Event Payload Format** (CloudEvents standard):
```json
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "/backend/tasks",
  "id": "<uuid>",
  "time": "2026-02-08T12:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "title": "Buy groceries"
  }
}
```

---

### 5. State Management Specification

**Data Suitable for Dapr State Store**:

| Data Type | Key Format | TTL | Purpose |
|-----------|-----------|-----|---------|
| Chat Session | `chat:session:{user_id}` | 3600s (1 hour) | Active conversation context |
| User Cache | `cache:user:{user_id}` | 1800s (30 min) | Cached user profile data |
| Workflow State | `workflow:task:{workflow_id}` | 600s (10 min) | Multi-step process state |
| Task Cache | `cache:tasks:{user_id}` | 300s (5 min) | Cached task list |

**Access Method via Dapr HTTP API**:

**Save State**:
```
POST http://localhost:3500/v1.0/state/statestore
Body: [{"key": "chat:session:123", "value": {...}, "metadata": {"ttlInSeconds": "3600"}}]
```

**Get State**:
```
GET http://localhost:3500/v1.0/state/statestore/chat:session:123
```

**Delete State**:
```
DELETE http://localhost:3500/v1.0/state/statestore/chat:session:123
```

**Bulk Get**:
```
POST http://localhost:3500/v1.0/state/statestore/bulk
Body: {"keys": ["cache:user:123", "cache:user:456"], "parallelism": 10}
```

---

### 6. Helm Chart Integration Specification

**Annotation Placement in Templates**:

**File**: `helm/todo-chart/templates/backend/deployment.yaml`
**Location**: `spec.template.metadata.annotations`
```yaml
{{- if .Values.dapr.enabled }}
dapr.io/enabled: "true"
dapr.io/app-id: {{ .Values.backend.dapr.appId | quote }}
dapr.io/app-port: {{ .Values.backend.dapr.appPort | quote }}
dapr.io/log-level: {{ .Values.dapr.logLevel | quote }}
dapr.io/enable-metrics: {{ .Values.dapr.enableMetrics | quote }}
{{- end }}
```

**Dapr Components in Helm Structure**:
```
helm/todo-chart/
├── templates/
│   ├── dapr-components/
│   │   ├── statestore.yaml
│   │   ├── pubsub.yaml
│   │   └── config.yaml (optional)
│   ├── frontend/
│   │   └── deployment.yaml (modified with annotations)
│   └── backend/
│       └── deployment.yaml (modified with annotations)
└── values.yaml (Dapr section added)
```

**values.yaml Parameterization Rules**:
```yaml
dapr:
  enabled: true
  logLevel: info
  enableMetrics: true

  stateStore:
    enabled: true
    type: state.redis
    redisHost: "redis-master.default.svc.cluster.local:6379"
    secretName: "redis-secret"
    secretKey: "password"

  pubsub:
    enabled: true
    type: pubsub.redis
    redisHost: "redis-master.default.svc.cluster.local:6379"
    secretName: "redis-secret"
    secretKey: "password"

frontend:
  dapr:
    appId: frontend-app
    appPort: 3000

backend:
  dapr:
    appId: backend-app
    appPort: 8000
```

---

### 7. Observability Specification

**Verify Sidecars Using `dapr list -k`**:
```bash
$ dapr list -k
APP ID         APP PORT  AGE  CREATED
frontend-app   3000      5m   2026-02-08 12:00.00
backend-app    8000      5m   2026-02-08 12:00.00
```

**Log Inspection Strategy**:

**View Dapr Sidecar Logs**:
```bash
kubectl logs <pod-name> -c daprd -n default --tail=100 -f
```

**Key Log Patterns to Verify**:
- Initialization: `"dapr initialized. Status: Running"`
- Component loading: `"component loaded. name: statestore, type: state.redis"`
- Service invocation: `"invoking target backend-app, method: /tasks"`

**Pod Verification Approach**:
```bash
# Check pod shows 2/2 containers
kubectl get pods -n default
# NAME                       READY   STATUS
# backend-7d8f9b5c-abcde     2/2     Running

# Describe pod to see both containers
kubectl describe pod <pod-name> -n default
# Should show containers: backend, daprd
```

**Component Status Check**:
```bash
kubectl get components -n default
# NAME         AGE
# statestore   5m
# pubsub       5m

kubectl describe component statestore -n default
```

---

### 8. Networking & Port Specification

**Dapr Port Usage**:
- HTTP Port: 3500 (default, used for all API calls)
- gRPC Port: 50001 (default, for high-performance invocations)
- Metrics Port: 9090 (Prometheus metrics endpoint)

**Internal Pod Communication Flow**:
```
Frontend Container (localhost:3000)
    ↓ HTTP call to localhost:3500
Frontend Dapr Sidecar (localhost:3500)
    ↓ Service invocation to backend-app
    ↓ Network call to backend pod
Backend Dapr Sidecar (receives on 50001)
    ↓ HTTP call to localhost:8000
Backend Container (localhost:8000)
```

**Environment Variables for Application**:
- `DAPR_HTTP_PORT=3500` (injected into app containers)
- `DAPR_GRPC_PORT=50001` (injected into app containers)
- Application code reads these to construct Dapr API URLs

---

### 9. Distributed Architecture Blueprint

**Reusable Helm Chart Structure**:
```
helm/{app-name}-chart/
├── Chart.yaml
├── values.yaml
│   └── dapr: {...}  # Dapr configuration section
├── templates/
│   ├── dapr-components/
│   │   ├── statestore.yaml
│   │   ├── pubsub.yaml
│   │   └── config.yaml
│   ├── {service1}/
│   │   ├── deployment.yaml  # With Dapr annotations
│   │   └── service.yaml
│   └── {service2}/
│       ├── deployment.yaml  # With Dapr annotations
│       └── service.yaml
└── README.md
```

**Generic Naming Conventions**:
- Component names: `statestore`, `pubsub` (generic, not app-specific)
- App-IDs: `{service-name}-app` pattern
- Topics: `{domain}.{entity}.{action}` pattern
- State keys: `{domain}:{type}:{identifier}` pattern

**Folder Structure Standards**:
- `/templates/dapr-components/` for all Dapr CRDs
- Separate deployment files for each service
- values.yaml has dedicated `dapr:` top-level section
- README documents Dapr prerequisites and configuration

---

### 10. Constraints

**No Business Logic Changes**:
- Task creation, update, delete logic remains identical
- Authentication and authorization unchanged
- Database queries and ORM usage unchanged
- API endpoint paths and contracts unchanged

**No API Contract Changes**:
- REST endpoint URLs remain the same (e.g., `/tasks`, `/auth/login`)
- Request/response payloads unchanged
- HTTP methods unchanged (GET, POST, PUT, DELETE)
- Status codes and error responses unchanged

**No Database Schema Changes**:
- Users, Tasks, Activities tables unchanged
- No new tables or columns added
- No migrations required
- Indexes and constraints unchanged

**Helm Deployability**:
- Single command deployment: `helm install todo-app ./helm/todo-chart`
- All configuration via values.yaml
- No manual kubectl apply steps required
- Backward compatible (can disable Dapr via flag)
