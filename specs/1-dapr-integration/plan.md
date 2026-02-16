# Implementation Plan: Dapr Infrastructure Integration

**Branch**: `1-dapr-integration` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-dapr-integration/spec.md`

**Note**: This implementation plan defines the stage-by-stage execution order to transform the Kubernetes-deployed Todo Application into a Dapr-powered distributed microservices architecture.

## Summary

Transform existing Kubernetes-deployed Todo Application (frontend + backend + PostgreSQL + AI chatbot) into a distributed, event-driven microservices architecture using Dapr building blocks. Integration introduces Dapr sidecars for service invocation, pub/sub components for event-driven task operations, state store for distributed caching, and Helm-managed deployment—all without modifying application business logic, API contracts, or database schemas.

**Technical Approach**: Infrastructure-only transformation using Dapr annotations, component YAMLs, and Helm chart modifications. Existing application code remains untouched except for adding Dapr SDK calls for pub/sub and state management (no business logic changes).

## Technical Context

**Language/Version**:
- Backend: Python 3.11 (FastAPI)
- Frontend: Node.js 18+ (Next.js 14)
- Infrastructure: YAML (Kubernetes manifests), Helm 3+

**Primary Dependencies**:
- Existing: FastAPI, Next.js, PostgreSQL (Neon), Kubernetes, Helm
- New (Phase V): Dapr 1.10+, Redis (for state store and pub/sub)

**Storage**:
- Primary: PostgreSQL (Neon) - unchanged
- New: Redis (Dapr state store and pub/sub broker)

**Testing**:
- Integration tests: Dapr CLI (`dapr list -k`), kubectl commands
- Functional tests: API endpoint verification through Dapr invocation
- Observability: Pod inspection (2/2 containers), component status

**Target Platform**:
- Development: Minikube (Kubernetes local cluster)
- Deployment: Kubernetes 1.19+ with Dapr runtime installed

**Project Type**: Web application (frontend + backend microservices)

**Performance Goals**:
- Service invocation latency increase: <50ms compared to direct HTTP
- Event delivery latency: <1 second from publish to subscribe
- State store operations: <100ms for get/set operations
- System throughput: Handle 1000 concurrent requests without degradation

**Constraints**:
- NO business logic modifications
- NO API contract changes
- NO database schema changes
- ALL changes must be Kubernetes-native and Helm-managed
- System must remain deployable via single `helm install` command

**Scale/Scope**:
- 2 services requiring Dapr sidecars (frontend, backend)
- 2 Dapr components (state store, pub/sub)
- 4 event types (task.created, task.updated, task.deleted, task.completed)
- 1 subscriber service (activity logging)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase V Constitution Compliance

✅ **Phase V Dapr Focus**: PASS
- Phases II, III, IV (application logic, APIs, Kubernetes infrastructure) remain unchanged
- Only Dapr capabilities being added (sidecars, components, invocation, pub/sub, state)
- All changes are Kubernetes-native and Helm-managed

✅ **Dapr-First Integration**: PASS
- All distributed capabilities introduced through Dapr building blocks
- Production-grade Kubernetes artifacts maintained
- Helm install remains single-command deployment

✅ **Service Communication Transformation**: PASS
- Plan includes converting direct API calls to Dapr service invocation
- Plan includes event-driven pub/sub patterns for task operations
- Plan includes distributed state management for chat/session data

✅ **Component Management Excellence**: PASS
- Dapr components will be Helm-managed
- Redis used for both state store and pub/sub (free, in-cluster)
- Components use Kubernetes Secrets for authentication
- Component scopes restrict access appropriately

✅ **Distributed Intelligence Without Rewriting**: PASS
- Dapr sidecars enabled via pod annotations only
- Application code may add Dapr SDK calls but no business logic changes
- All infrastructure transformations are non-invasive

### Hard Constraints Compliance

✅ **Constraint 1**: DO NOT modify business logic - PASS (only infrastructure changes)
✅ **Constraint 2**: DO NOT change database schemas - PASS (PostgreSQL unchanged)
✅ **Constraint 3**: DO NOT break Kubernetes/Helm setup - PASS (extends existing setup)
✅ **Constraint 4**: ONLY extend using Dapr capabilities - PASS (all changes Dapr-related)
✅ **Constraint 5**: All changes Kubernetes-native and Helm-managed - PASS
✅ **Constraint 6**: NO hardcoded secrets - PASS (using Kubernetes Secrets)
✅ **Constraint 7**: Dapr enabled via pod annotations only - PASS
✅ **Constraint 8**: Redis for state/pubsub - PASS (Redis chosen)
✅ **Constraint 9**: Demonstrate invocation + events - PASS (both included)
✅ **Constraint 10**: Helm install functional - PASS (backward compatible)

**Gate Result**: ✅ ALL CHECKS PASSED - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/1-dapr-integration/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── statestore-component.yaml
│   ├── pubsub-component.yaml
│   ├── dapr-config.yaml
│   └── events-schema.json
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Existing structure (unchanged)
backend/
├── src/
│   ├── ai/              # Chatbot components
│   ├── api/             # FastAPI routers
│   ├── models/          # SQLModel models
│   ├── services/        # Business logic
│   └── utils/           # Utilities
│       └── dapr/        # NEW: Dapr client utilities (added)
└── tests/

frontend/
├── src/
│   ├── app/             # Next.js App Router
│   ├── components/      # React components
│   └── lib/             # Utilities
│       └── dapr/        # NEW: Dapr client utilities (added)
└── tests/

# Helm chart structure (modified)
helm/todo-chart/
├── Chart.yaml           # Version incremented
├── values.yaml          # NEW: Dapr section added
└── templates/
    ├── _helpers.tpl     # NEW: Dapr annotation helpers
    ├── frontend-deployment.yaml  # MODIFIED: Dapr annotations
    ├── frontend-service.yaml     # Unchanged
    ├── backend-deployment.yaml   # MODIFIED: Dapr annotations
    ├── backend-service.yaml      # Unchanged
    ├── configmap.yaml            # Unchanged
    ├── secrets.yaml              # Unchanged
    └── dapr-components/          # NEW: Directory for Dapr CRDs
        ├── statestore.yaml
        ├── pubsub.yaml
        └── config.yaml (optional)
```

**Structure Decision**: Web application structure with frontend and backend services. Helm chart extended with new `dapr-components/` directory for Dapr CRDs. Application source code extended with optional `utils/dapr/` directories for Dapr client helpers (non-invasive additions).

## Complexity Tracking

> No constitutional violations - all changes comply with Phase V requirements.

---

## Phase 0: Research & Discovery

### Research Tasks

#### Research Task 1: Dapr Installation and Prerequisites
**Objective**: Verify Dapr runtime installation on Minikube and document prerequisites

**Research Questions**:
- Is Dapr runtime installed on the Minikube cluster? (`dapr status -k`)
- What version of Dapr is required (minimum 1.10+)?
- What are the namespace requirements (default namespace assumed)?
- Are there any missing Dapr components in the control plane?

**Expected Findings**:
- Dapr control plane status (operator, sidecar-injector, placement, sentry, dashboard)
- Dapr version compatibility with Kubernetes 1.19+
- Prerequisites checklist for Dapr enablement

#### Research Task 2: Redis Infrastructure Analysis
**Objective**: Identify Redis deployment options and connection strategies

**Research Questions**:
- Is Redis already deployed in the cluster?
- Should Redis be deployed as part of Helm chart or assumed pre-existing?
- What are the Redis authentication requirements (password, TLS)?
- What is the Redis connection string format for Dapr components?

**Expected Findings**:
- Redis deployment strategy (in-cluster Helm subchart vs. external)
- Redis connection details (host, port, authentication method)
- Kubernetes Secret structure for Redis credentials

#### Research Task 3: Existing Helm Chart Analysis
**Objective**: Understand current Helm chart structure and modification points

**Research Questions**:
- What is the current structure of `helm/todo-chart/templates/`?
- How are deployment annotations currently managed?
- What is the naming convention for templates (frontend-deployment.yaml, backend-deployment.yaml)?
- Are there existing helper templates in `_helpers.tpl`?

**Expected Findings**:
- Current deployment YAML structure
- Template naming conventions
- Existing annotation patterns
- values.yaml structure and organization

#### Research Task 4: Dapr Annotation Best Practices
**Objective**: Research standard Dapr annotation patterns for Kubernetes

**Research Questions**:
- What are the minimal required Dapr annotations (`dapr.io/enabled`, `dapr.io/app-id`, `dapr.io/app-port`)?
- What are optional but recommended annotations (`dapr.io/log-level`, `dapr.io/enable-metrics`)?
- How should app-id naming conventions be structured?
- What are the default Dapr ports (HTTP 3500, gRPC 50001)?

**Expected Findings**:
- Complete list of Dapr pod annotations
- Naming conventions for app-ids
- Port configuration standards
- Metrics and observability settings

#### Research Task 5: Dapr Component YAML Structure
**Objective**: Research Dapr component CRD structure and best practices

**Research Questions**:
- What is the YAML structure for `state.redis` components?
- What is the YAML structure for `pubsub.redis` components?
- How are component scopes defined and enforced?
- How are Kubernetes Secrets referenced in component metadata?

**Expected Findings**:
- Component YAML templates for state store and pub/sub
- Metadata field requirements (redisHost, redisPassword, consumerID)
- Scoping mechanisms (which apps can access which components)
- Secret reference patterns

#### Research Task 6: Service Invocation Patterns
**Objective**: Research Dapr service invocation API and migration strategy

**Research Questions**:
- What is the URL format for Dapr HTTP invocation (`/v1.0/invoke/{app-id}/method/{path}`)?
- How are HTTP headers propagated through Dapr invocation?
- What are the error handling patterns for service invocation?
- What is the performance overhead of Dapr invocation vs. direct HTTP?

**Expected Findings**:
- Service invocation URL templates
- Header propagation behavior
- Error codes and retry mechanisms
- Performance benchmarks (<50ms overhead expected)

#### Research Task 7: Pub/Sub Event Patterns
**Objective**: Research Dapr pub/sub patterns and CloudEvents standard

**Research Questions**:
- What is the CloudEvents specification structure?
- How are topics named in Dapr pub/sub (`domain.entity.action`)?
- How are subscriptions configured (`/dapr/subscribe` endpoint)?
- What are the retry policies and dead letter queue configurations?

**Expected Findings**:
- CloudEvents JSON schema
- Topic naming conventions
- Subscription configuration examples
- Retry and DLQ patterns

#### Research Task 8: State Store Access Patterns
**Objective**: Research Dapr state management API and key naming conventions

**Research Questions**:
- What is the HTTP API format for state operations (`/v1.0/state/{storename}`)?
- How are TTL (time-to-live) values configured in metadata?
- What are the key naming conventions (`domain:type:identifier`)?
- How are bulk operations performed?

**Expected Findings**:
- State store HTTP API documentation
- TTL metadata structure
- Key naming best practices
- Bulk operation examples

### Research Output

**File**: `specs/1-dapr-integration/research.md`

**Contents**:
- Decision log for each research task
- Rationale for technical choices
- Alternatives considered and rejected
- Prerequisites checklist
- Component YAML templates discovered
- API patterns and examples
- Performance considerations
- Security implications

**Validation Criteria**:
- All NEEDS CLARIFICATION items resolved
- Dapr installation prerequisites documented
- Redis connection strategy decided
- Annotation patterns finalized
- Component structures validated
- Service invocation patterns confirmed
- Pub/sub patterns confirmed
- State management patterns confirmed

---

## Phase 1: Design & Contracts

### Phase 1.1: Data Model Design

**File**: `specs/1-dapr-integration/data-model.md`

**Entities** (infrastructure-focused, not application data):

#### Entity 1: Dapr Sidecar Configuration
- **Attributes**: app-id, app-port, log-level, enable-metrics, metrics-port
- **Relationships**: Injected into frontend and backend deployment pods
- **Validation**: app-id must match component scopes, app-port must match container port
- **Lifecycle**: Managed by Kubernetes via annotations

#### Entity 2: Dapr Component (State Store)
- **Attributes**: name (statestore), type (state.redis), version (v1), metadata, scopes
- **Relationships**: Referenced by backend app for state operations
- **Validation**: Redis connection must be valid, scopes must match app-ids
- **Lifecycle**: Deployed via Helm, managed as Kubernetes CRD

#### Entity 3: Dapr Component (Pub/Sub)
- **Attributes**: name (pubsub), type (pubsub.redis), version (v1), metadata, scopes
- **Relationships**: Used by backend for publishing, activity service for subscribing
- **Validation**: Redis connection must be valid, consumerID must be unique
- **Lifecycle**: Deployed via Helm, managed as Kubernetes CRD

#### Entity 4: CloudEvent
- **Attributes**: specversion, type, source, id, time, datacontenttype, data
- **Relationships**: Published to pub/sub topics, consumed by subscribers
- **Validation**: Must conform to CloudEvents 1.0 specification
- **State Transitions**: Published → Queued → Delivered → Acknowledged

#### Entity 5: State Store Entry
- **Attributes**: key, value, etag, metadata (ttlInSeconds)
- **Relationships**: Stored in Redis via Dapr state API
- **Validation**: Key must follow naming convention, TTL must be positive integer
- **Lifecycle**: Created → Active → Expired (based on TTL)

### Phase 1.2: Contract Generation

**Directory**: `specs/1-dapr-integration/contracts/`

#### Contract 1: State Store Component YAML
**File**: `statestore-component.yaml`
```yaml
# Full production-ready state store component definition
# Includes Redis connection, authentication, scoping
```

#### Contract 2: Pub/Sub Component YAML
**File**: `pubsub-component.yaml`
```yaml
# Full production-ready pub/sub component definition
# Includes Redis Streams configuration, consumer group, scoping
```

#### Contract 3: Dapr Configuration YAML (Optional)
**File**: `dapr-config.yaml`
```yaml
# Optional Dapr Configuration for tracing, metrics, mTLS
# Can be added in later phase if needed
```

#### Contract 4: Event Schemas
**File**: `events-schema.json`
```json
{
  "task.created": {
    "specversion": "1.0",
    "type": "task.created",
    "source": "/backend/tasks",
    "data": {
      "task_id": "integer",
      "user_id": "integer",
      "title": "string",
      "created_at": "ISO8601"
    }
  },
  "task.updated": { ... },
  "task.deleted": { ... },
  "task.completed": { ... }
}
```

#### Contract 5: Helm values.yaml Dapr Section
**File**: `values-dapr-section.yaml`
```yaml
# Complete Dapr configuration section for values.yaml
# Includes flags, component configs, app-id mappings
```

### Phase 1.3: Quickstart Guide

**File**: `specs/1-dapr-integration/quickstart.md`

**Contents**:
- Prerequisites checklist (Dapr installed, Redis available)
- Step-by-step Helm upgrade instructions
- Verification commands (`dapr list -k`, `kubectl get pods`, `kubectl get components`)
- Rollback procedures if needed
- Troubleshooting common issues
- Expected output examples

### Phase 1.4: Agent Context Update

**Action**: Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

**Result**: Updates Claude-specific context file with:
- New technologies: Dapr 1.10+, Redis (state/pubsub)
- New patterns: Sidecar injection, service invocation, pub/sub, state management
- Preserves existing manual additions

**Validation**: Agent context file includes Dapr-specific guidance

---

## Phase 2: Implementation Stages

### Stage 1 — Dapr Environment Preparation

**Objective**: Verify Dapr runtime is installed and prerequisites are met

**Responsible Agent(s)**: `dapr-observability-agent`

**Skills Used**:
- `dapr-observability-skill`: Verify Dapr control plane status

**Expected Output**:
- Dapr status verification report
- Prerequisites checklist (completed)
- Namespace confirmation (default namespace ready)
- Dapr version confirmation (1.10+ installed)

**Validation Criteria**:
```bash
# Must pass before proceeding
dapr status -k
# Expected: All control plane components (operator, sidecar-injector, placement, sentry) running

kubectl get namespace default
# Expected: Namespace exists

dapr version
# Expected: CLI version and runtime version both 1.10+
```

**Deliverables**:
- [ ] Dapr control plane running and healthy
- [ ] Default namespace ready
- [ ] Dapr CLI accessible
- [ ] Prerequisites documented

---

### Stage 2 — Redis Infrastructure Setup

**Objective**: Deploy or verify Redis instance for Dapr components

**Responsible Agent(s)**: `distributed-architecture-agent`

**Skills Used**:
- `distributed-config-skill`: Configure Redis connection
- `env-secrets-config-skill`: Create Kubernetes Secret for Redis password

**Expected Output**:
- Redis deployment (if not existing) via Helm subchart or manual deployment
- Kubernetes Secret created: `redis-secret` with key `password`
- Redis connection string documented: `redis-master.default.svc.cluster.local:6379`

**Validation Criteria**:
```bash
# Redis must be accessible
kubectl get pods | grep redis
# Expected: Redis pod running

kubectl get secret redis-secret
# Expected: Secret exists with password key

# Test Redis connection from within cluster
kubectl run redis-test --rm -it --image=redis:latest -- redis-cli -h redis-master.default.svc.cluster.local -a <password> ping
# Expected: PONG
```

**Deliverables**:
- [ ] Redis instance running and accessible
- [ ] Kubernetes Secret `redis-secret` created
- [ ] Redis connection tested successfully
- [ ] Connection string documented in Helm values

---

### Stage 3 — Dapr Component Creation

**Objective**: Create Dapr component YAMLs for state store and pub/sub

**Responsible Agent(s)**: `dapr-component-agent`

**Skills Used**:
- `dapr-component-state-store-skill`: Create state store component YAML
- `dapr-component-pubsub-skill`: Create pub/sub component YAML

**Expected Output**:
- File: `helm/todo-chart/templates/dapr-components/statestore.yaml`
  - Component name: `statestore`
  - Type: `state.redis`
  - Scopes: `[backend-app]`
  - Metadata: redisHost, redisPassword (from Secret)

- File: `helm/todo-chart/templates/dapr-components/pubsub.yaml`
  - Component name: `pubsub`
  - Type: `pubsub.redis`
  - Scopes: `[backend-app]`
  - Metadata: redisHost, redisPassword (from Secret), consumerID

**Validation Criteria**:
```bash
# Validate YAML syntax
kubectl apply --dry-run=client -f helm/todo-chart/templates/dapr-components/statestore.yaml
kubectl apply --dry-run=client -f helm/todo-chart/templates/dapr-components/pubsub.yaml
# Expected: No errors

# Check component structure
cat helm/todo-chart/templates/dapr-components/statestore.yaml
# Expected: Valid Dapr Component CRD with correct apiVersion, kind, metadata, spec
```

**Deliverables**:
- [ ] statestore.yaml created with correct structure
- [ ] pubsub.yaml created with correct structure
- [ ] Components reference Kubernetes Secret correctly
- [ ] Scopes configured appropriately
- [ ] YAML syntax validated

---

### Stage 4 — Helm Chart Integration

**Objective**: Integrate Dapr components and annotations into Helm chart

**Responsible Agent(s)**: `dapr-helm-integration-agent`

**Skills Used**:
- `dapr-helm-integration-skill`: Add Dapr section to values.yaml
- `dapr-sidecar-annotation-skill`: Add annotations to deployment templates

**Expected Output**:

#### 4.1: values.yaml Update
- New section added:
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

#### 4.2: frontend-deployment.yaml Update
- Annotations added to `spec.template.metadata.annotations`:
```yaml
{{- if .Values.dapr.enabled }}
dapr.io/enabled: "true"
dapr.io/app-id: {{ .Values.frontend.dapr.appId | quote }}
dapr.io/app-port: {{ .Values.frontend.dapr.appPort | quote }}
dapr.io/log-level: {{ .Values.dapr.logLevel | quote }}
dapr.io/enable-metrics: {{ .Values.dapr.enableMetrics | quote }}
{{- end }}
```

#### 4.3: backend-deployment.yaml Update
- Same annotation pattern as frontend

#### 4.4: _helpers.tpl Update (Optional)
- Helper template for Dapr annotations to reduce duplication

**Validation Criteria**:
```bash
# Validate Helm template rendering
helm template todo-app ./helm/todo-chart --set dapr.enabled=true
# Expected: Dapr annotations appear in rendered deployments

# Validate with Helm lint
helm lint ./helm/todo-chart
# Expected: No errors or warnings

# Dry-run install
helm install todo-app ./helm/todo-chart --dry-run --debug
# Expected: All templates render correctly, components included
```

**Deliverables**:
- [ ] values.yaml updated with Dapr section
- [ ] frontend-deployment.yaml has conditional Dapr annotations
- [ ] backend-deployment.yaml has conditional Dapr annotations
- [ ] dapr-components/ directory included in Helm package
- [ ] Helm lint passes
- [ ] Dry-run install succeeds

---

### Stage 5 — Sidecar Enablement Deployment

**Objective**: Deploy Helm chart with Dapr enabled and verify sidecar injection

**Responsible Agent(s)**: `dapr-enable-agent`

**Skills Used**:
- `dapr-sidecar-annotation-skill`: Verify annotations trigger injection
- `dapr-helm-integration-skill`: Deploy via Helm

**Expected Output**:
- Helm upgrade executed: `helm upgrade todo-app ./helm/todo-chart --set dapr.enabled=true`
- Pods restarted with Dapr sidecars
- Each pod shows 2/2 containers (app + daprd)

**Validation Criteria**:
```bash
# Check pod status
kubectl get pods -n default
# Expected output:
# NAME                       READY   STATUS    RESTARTS
# frontend-xxx-xxx           2/2     Running   0
# backend-xxx-xxx            2/2     Running   0

# Verify Dapr sidecar container exists
kubectl describe pod <frontend-pod> | grep daprd
kubectl describe pod <backend-pod> | grep daprd
# Expected: daprd container listed

# Check Dapr application registry
dapr list -k
# Expected output:
# APP ID         APP PORT  AGE  CREATED
# frontend-app   3000      1m   2026-02-08 12:00.00
# backend-app    8000      1m   2026-02-08 12:00.00

# Check Dapr sidecar logs
kubectl logs <backend-pod> -c daprd --tail=20
# Expected: "dapr initialized. Status: Running"
```

**Deliverables**:
- [ ] Helm upgrade completed successfully
- [ ] All pods show 2/2 containers
- [ ] `dapr list -k` shows both apps
- [ ] Dapr sidecar logs show initialization success
- [ ] No pod crash loops or errors

---

### Stage 6 — Dapr Components Deployment Verification

**Objective**: Verify Dapr components are deployed and functional

**Responsible Agent(s)**: `dapr-observability-agent`

**Skills Used**:
- `dapr-observability-skill`: Verify component status

**Expected Output**:
- Components deployed as Kubernetes CRDs
- Components show CREATED status
- Component logs show successful connection to Redis

**Validation Criteria**:
```bash
# Check component status
kubectl get components -n default
# Expected output:
# NAME         AGE
# statestore   2m
# pubsub       2m

# Describe components for details
kubectl describe component statestore -n default
# Expected: Type: state.redis, no error events

kubectl describe component pubsub -n default
# Expected: Type: pubsub.redis, no error events

# Check Dapr operator logs for component loading
kubectl logs -l app=dapr-operator -n dapr-system --tail=50
# Expected: "component loaded. name: statestore, type: state.redis"
# Expected: "component loaded. name: pubsub, type: pubsub.redis"

# Test state store access from backend pod
kubectl exec <backend-pod> -c backend -- curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key":"test","value":"hello"}]'
# Expected: 204 No Content (success)

kubectl exec <backend-pod> -c backend -- curl http://localhost:3500/v1.0/state/statestore/test
# Expected: "hello"
```

**Deliverables**:
- [ ] Components visible via `kubectl get components`
- [ ] No error events in component descriptions
- [ ] State store accessible via Dapr API
- [ ] Pub/sub component loaded successfully
- [ ] Redis connections established

---

### Stage 7 — Service Invocation Implementation

**Objective**: Implement Dapr service invocation between frontend and backend

**Responsible Agent(s)**: `service-invocation-agent`

**Skills Used**:
- `dapr-service-invocation-skill`: Implement invocation pattern
- `microservice-boundary-analysis-skill`: Identify service call points

**Expected Output**:

#### 7.1: Frontend Code Update (Optional Enhancement)
- Environment variable update: `NEXT_PUBLIC_API_BASE_URL=http://localhost:3500/v1.0/invoke/backend-app/method`
- API client code adjusted to use Dapr invocation format
- **Note**: This is optional; frontend can continue using Kubernetes service name if preferred

#### 7.2: Backend-to-Backend Invocation (If Applicable)
- Any internal service-to-service calls converted to Dapr invocation
- Example: If chatbot service needs to call task service

**Validation Criteria**:
```bash
# Test service invocation from frontend pod
kubectl exec <frontend-pod> -c frontend -- curl http://localhost:3500/v1.0/invoke/backend-app/method/health
# Expected: Backend health check response

# Check Dapr sidecar logs for invocation
kubectl logs <frontend-pod> -c daprd --tail=50 | grep invoke
# Expected: "invoking target backend-app, method: /health"

kubectl logs <backend-pod> -c daprd --tail=50 | grep invoke
# Expected: Logs showing incoming invocation

# Test end-to-end via frontend service
kubectl port-forward service/frontend 3000:3000
curl http://localhost:3000/api/tasks
# Expected: Task list returned (routed through Dapr)
```

**Deliverables**:
- [ ] Service invocation working between frontend and backend
- [ ] Dapr logs confirm invocation flow
- [ ] Application functionality unchanged
- [ ] No direct pod-to-pod HTTP calls (if desired migration level)
- [ ] Response times acceptable (<50ms overhead)

---

### Stage 8 — Pub/Sub Event Architecture Implementation

**Objective**: Implement event publishing and subscription for task operations

**Responsible Agent(s)**: `event-pubsub-agent`

**Skills Used**:
- `dapr-pubsub-publish-skill`: Implement event publishing
- `dapr-pubsub-subscribe-skill`: Implement event subscription
- `event-driven-architecture-skill`: Design event flow

**Expected Output**:

#### 8.1: Event Publisher (Backend)
- Code added to publish events after task operations:
  - `task.created` - after POST /tasks
  - `task.updated` - after PUT /tasks/{id}
  - `task.deleted` - after DELETE /tasks/{id}
  - `task.completed` - after marking task complete

```python
# Example: backend/src/utils/dapr/event_publisher.py
async def publish_task_created(task_id, user_id, title):
    event = {
        "specversion": "1.0",
        "type": "task.created",
        "source": "/backend/tasks",
        "id": str(uuid.uuid4()),
        "time": datetime.utcnow().isoformat() + "Z",
        "data": {"task_id": task_id, "user_id": user_id, "title": title}
    }
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/publish/pubsub/task.created",
            json=event
        )
```

#### 8.2: Event Subscriber (Activity Service - Existing Backend Endpoint)
- Subscription endpoint created: `/dapr/subscribe`
- Event handler endpoint: `/events/task-created`

```python
# backend/src/api/events_router.py
@router.get("/dapr/subscribe")
async def subscribe():
    return [
        {"pubsubname": "pubsub", "topic": "task.created", "route": "/events/task-created"},
        {"pubsubname": "pubsub", "topic": "task.updated", "route": "/events/task-updated"},
        {"pubsubname": "pubsub", "topic": "task.deleted", "route": "/events/task-deleted"},
        {"pubsubname": "pubsub", "topic": "task.completed", "route": "/events/task-completed"}
    ]

@router.post("/events/task-created")
async def handle_task_created(request: Request):
    event = await request.json()
    # Log activity
    await log_activity(event["data"])
    return {"status": "SUCCESS"}
```

**Validation Criteria**:
```bash
# Test event publishing
# Create a task via API
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Test Task","user_id":1}'

# Check backend logs for publish confirmation
kubectl logs <backend-pod> -c backend | grep "published"
# Expected: Event published log

# Check Dapr sidecar logs for pub/sub activity
kubectl logs <backend-pod> -c daprd | grep pubsub
# Expected: "published message to topic: task.created"

# Check subscriber endpoint
kubectl exec <backend-pod> -c backend -- curl http://localhost:8000/dapr/subscribe
# Expected: JSON array with subscription definitions

# Verify event was delivered to subscriber
kubectl logs <backend-pod> -c backend | grep "task-created"
# Expected: Handler log showing event received
```

**Deliverables**:
- [ ] Event publishing implemented for all task operations
- [ ] Subscription endpoint configured
- [ ] Event handler endpoints implemented
- [ ] Events flow from publisher to subscriber
- [ ] Activity logging captures events successfully
- [ ] CloudEvents format validated

---

### Stage 9 — State Store Implementation

**Objective**: Implement distributed state management for chat and session data

**Responsible Agent(s)**: `state-management-agent`

**Skills Used**:
- `dapr-state-management-skill`: Implement state operations

**Expected Output**:

#### 9.1: State Store Client Utility
```python
# backend/src/utils/dapr/state_manager.py
class DaprStateManager:
    def __init__(self, state_store_name="statestore"):
        self.dapr_url = "http://localhost:3500"
        self.state_store_name = state_store_name

    async def save_state(self, key, value, ttl_seconds=None):
        metadata = {"ttlInSeconds": str(ttl_seconds)} if ttl_seconds else {}
        state_data = [{"key": key, "value": value, "metadata": metadata}]
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.dapr_url}/v1.0/state/{self.state_store_name}",
                json=state_data
            )
            return response.status_code == 204

    async def get_state(self, key):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.dapr_url}/v1.0/state/{self.state_store_name}/{key}"
            )
            if response.status_code == 204:
                return None
            return response.json()

    async def delete_state(self, key):
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.dapr_url}/v1.0/state/{self.state_store_name}/{key}"
            )
            return response.status_code == 204
```

#### 9.2: State Usage Examples
- Chat session storage: `chat:session:{user_id}` with 1-hour TTL
- User cache: `cache:user:{user_id}` with 30-minute TTL
- Workflow state: `workflow:task:{workflow_id}` with 10-minute TTL

**Validation Criteria**:
```bash
# Test state store operations
kubectl exec <backend-pod> -c backend -- curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key":"chat:session:123","value":{"messages":["hello"]},"metadata":{"ttlInSeconds":"3600"}}]'
# Expected: 204 No Content

# Retrieve state
kubectl exec <backend-pod> -c backend -- curl http://localhost:3500/v1.0/state/statestore/chat:session:123
# Expected: {"messages":["hello"]}

# Verify TTL expiration (after 1 hour)
# Expected: State no longer accessible

# Check state store metrics
kubectl logs <backend-pod> -c daprd | grep state
# Expected: State operations logged
```

**Deliverables**:
- [ ] State manager utility class implemented
- [ ] Chat session storage implemented with TTL
- [ ] User cache implemented with TTL
- [ ] State operations functional (save, get, delete)
- [ ] TTL expiration working correctly
- [ ] Key naming conventions followed

---

### Stage 10 — Observability & Verification

**Objective**: Set up comprehensive observability and validate all Dapr features

**Responsible Agent(s)**: `dapr-observability-agent`

**Skills Used**:
- `dapr-observability-skill`: Comprehensive monitoring setup

**Expected Output**:

#### 10.1: Verification Checklist
```bash
# 1. Verify Dapr sidecars
dapr list -k
# Expected: All services listed

# 2. Verify pod status
kubectl get pods -n default
# Expected: All pods 2/2 Ready

# 3. Verify components
kubectl get components -n default
# Expected: statestore, pubsub listed

# 4. Check component health
kubectl describe component statestore
kubectl describe component pubsub
# Expected: No error events

# 5. Test service invocation
kubectl exec <frontend-pod> -- curl http://localhost:3500/v1.0/invoke/backend-app/method/health
# Expected: 200 OK

# 6. Test pub/sub
# Publish test event
kubectl exec <backend-pod> -- curl -X POST http://localhost:3500/v1.0/publish/pubsub/test-topic \
  -H "Content-Type: application/json" -d '{"test":"data"}'
# Expected: 204 No Content

# 7. Test state store
# Already tested in Stage 9

# 8. Check logs for errors
kubectl logs <backend-pod> -c daprd --tail=100 | grep error
# Expected: No critical errors

# 9. Validate metrics endpoint
kubectl exec <backend-pod> -- curl http://localhost:9090/metrics
# Expected: Prometheus metrics

# 10. Full application smoke test
kubectl port-forward service/frontend 3000:3000
curl http://localhost:3000/api/tasks
# Expected: Application functioning normally
```

#### 10.2: Distributed Tracing Setup (Optional)
- Dapr Configuration with Zipkin endpoint (if tracing desired)
- Verification: Traces appear in Zipkin UI showing request flow

**Validation Criteria**:
- All 10 verification checks pass
- No pod restarts or crash loops
- Dapr sidecar logs clean
- Application functionality unchanged
- Performance within acceptable limits

**Deliverables**:
- [ ] All verification checks passing
- [ ] Observability documentation updated
- [ ] Troubleshooting guide created
- [ ] Metrics collection confirmed
- [ ] System stable and healthy

---

### Stage 11 — Distributed Architecture Generalization

**Objective**: Document and package reusable Dapr integration patterns

**Responsible Agent(s)**: `distributed-architecture-agent`

**Skills Used**:
- `event-driven-architecture-skill`: Document patterns
- `distributed-config-skill`: Generalize configuration
- `cloud-native-blueprint-skill`: Create reusable blueprint

**Expected Output**:

#### 11.1: Reusable Helm Chart Template
- Document how `helm/todo-chart/` structure can be replicated
- Generic naming conventions documented
- values.yaml template with clear comments
- Component templates with placeholders

#### 11.2: Dapr Integration Guide
**File**: `docs/DAPR_INTEGRATION_GUIDE.md`
- Step-by-step guide to add Dapr to any Helm chart
- Annotation patterns
- Component creation workflow
- values.yaml structure
- Verification checklist

#### 11.3: Distributed Architecture Blueprint
**File**: `docs/DISTRIBUTED_ARCHITECTURE_BLUEPRINT.md`
- Service decomposition patterns
- Communication patterns (sync vs. async)
- Event-driven design principles
- State management strategies
- Observability setup

**Validation Criteria**:
- Documentation is clear and comprehensive
- Patterns are generalized (not todo-app-specific)
- Examples are provided
- Prerequisites are documented
- Troubleshooting section included

**Deliverables**:
- [ ] Dapr integration guide created
- [ ] Distributed architecture blueprint documented
- [ ] Reusable templates extracted
- [ ] Best practices documented
- [ ] Examples provided

---

### Stage 12 — Final Validation & Success Criteria

**Objective**: Validate all success criteria from specification

**Responsible Agent(s)**: Multiple agents for comprehensive validation

**Skills Used**: All observability and verification skills

**Success Criteria Validation**:

#### SC-001: Each pod shows 2/2 containers
```bash
kubectl get pods -n default
# PASS if all pods show 2/2 in READY column
```

#### SC-002: `dapr list -k` returns all services within 5 seconds
```bash
time dapr list -k
# PASS if completes in <5 seconds and shows all services
```

#### SC-003: Latency increase <50ms with Dapr
```bash
# Measure direct call latency
time curl http://backend-service:8000/health

# Measure Dapr invocation latency
kubectl exec <frontend-pod> -- bash -c "time curl http://localhost:3500/v1.0/invoke/backend-app/method/health"

# PASS if difference <50ms
```

#### SC-004: Events delivered within 1 second
```bash
# Publish event with timestamp, check subscriber log timestamp
# PASS if delivery latency <1 second
```

#### SC-005: State persists and expires per TTL
```bash
# Save state with TTL, verify retrieval, wait for expiration
# PASS if state expires correctly
```

#### SC-006: Single `helm install` command deployment
```bash
helm uninstall todo-app
helm install todo-app ./helm/todo-chart
kubectl wait --for=condition=ready pod --all --timeout=300s
# PASS if deployment succeeds
```

#### SC-007: Components show CREATED status
```bash
kubectl get components -n default
# PASS if statestore and pubsub listed
```

#### SC-008: Distributed traces visible
```bash
# If tracing enabled, check Zipkin UI
# PASS if traces appear
```

#### SC-009: 1000 concurrent requests without degradation
```bash
# Load test (optional for Phase V)
# PASS if system handles load
```

#### SC-010: 100% functionality preserved
```bash
# Run full application test suite
# PASS if all tests pass, no regressions
```

**Validation Criteria**:
- All 10 success criteria pass
- No functional regressions
- Performance acceptable
- System stable

**Deliverables**:
- [ ] All success criteria validated
- [ ] Validation report created
- [ ] Any issues documented
- [ ] Sign-off for Phase V completion

---

## Phase 3: Task Breakdown (Not Created by This Command)

**Note**: Task breakdown is created by `/sp.tasks` command, not `/sp.plan`.

Task file will include:
- Atomic implementation tasks for each stage
- Acceptance tests for each task
- Dependencies between tasks
- Estimated effort per task

---

## Risk Analysis

### Risk 1: Dapr Not Installed on Minikube
**Impact**: HIGH - Cannot proceed without Dapr runtime
**Mitigation**: Verify in Stage 1, install if missing: `dapr init -k`
**Fallback**: Detailed installation documentation provided

### Risk 2: Redis Not Available
**Impact**: HIGH - Dapr components cannot function
**Mitigation**: Check in Stage 2, deploy Redis via Helm subchart if needed
**Fallback**: Use external Redis service

### Risk 3: Sidecar Injection Fails
**Impact**: MEDIUM - Pods won't have Dapr capabilities
**Mitigation**: Validate annotations in Stage 4 dry-run, check Dapr operator logs
**Fallback**: Manually troubleshoot injection issues, verify namespace labels

### Risk 4: Component Connection Failures
**Impact**: MEDIUM - State store or pub/sub not functional
**Mitigation**: Test Redis connectivity in Stage 6, validate credentials
**Fallback**: Review component logs, fix connection strings

### Risk 5: Performance Degradation
**Impact**: LOW - Acceptable as long as <50ms overhead
**Mitigation**: Monitor in Stage 10, benchmark if needed
**Fallback**: Tune Dapr sidecar resource limits

### Risk 6: Application Code Breaking Changes
**Impact**: CRITICAL - Violates Phase V Constitution
**Mitigation**: All code changes reviewed against "no business logic" rule
**Fallback**: Revert any invasive changes, stick to infrastructure only

---

## Next Steps After Plan Completion

1. **Run `/sp.tasks`**: Generate detailed task breakdown from this plan
2. **Review Tasks**: Validate task dependencies and acceptance criteria
3. **Begin Implementation**: Execute tasks in order following stages
4. **Continuous Validation**: Run verification checks after each stage
5. **Documentation**: Keep quickstart and troubleshooting guides updated

---

## Appendix A: Dapr Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                     Frontend Pod                                │
│  ┌──────────────────┐           ┌─────────────────────┐       │
│  │  Next.js App     │◄─────────►│  Dapr Sidecar       │       │
│  │  (Port 3000)     │ localhost │  (HTTP: 3500)       │       │
│  │                  │           │  (gRPC: 50001)      │       │
│  └──────────────────┘           └──────────┬──────────┘       │
└─────────────────────────────────────────────┼──────────────────┘
                                               │
                                               │ Service Invocation
                                               ▼
┌────────────────────────────────────────────────────────────────┐
│                     Backend Pod                                 │
│  ┌──────────────────┐           ┌─────────────────────┐       │
│  │  FastAPI App     │◄─────────►│  Dapr Sidecar       │       │
│  │  (Port 8000)     │ localhost │  (HTTP: 3500)       │       │
│  │                  │           │  (gRPC: 50001)      │       │
│  └──────────────────┘           └──────────┬──────────┘       │
└─────────────────────────────────────────────┼──────────────────┘
                                               │
                      ┌────────────────────────┼────────────────────────┐
                      │                        │                        │
                      ▼                        ▼                        ▼
            ┌─────────────────┐    ┌──────────────────┐    ┌───────────────────┐
            │  State Store    │    │  Pub/Sub         │    │  Service          │
            │  Component      │    │  Component       │    │  Invocation       │
            │  (Redis)        │    │  (Redis Streams) │    │  (mTLS optional)  │
            └─────────────────┘    └──────────────────┘    └───────────────────┘
```

---

## Appendix B: File Modification Summary

| File Path | Modification Type | Description |
|-----------|------------------|-------------|
| `helm/todo-chart/values.yaml` | MODIFIED | Added `dapr:` section |
| `helm/todo-chart/templates/frontend-deployment.yaml` | MODIFIED | Added conditional Dapr annotations |
| `helm/todo-chart/templates/backend-deployment.yaml` | MODIFIED | Added conditional Dapr annotations |
| `helm/todo-chart/templates/_helpers.tpl` | MODIFIED (optional) | Added Dapr annotation helpers |
| `helm/todo-chart/templates/dapr-components/statestore.yaml` | CREATED | State store component CRD |
| `helm/todo-chart/templates/dapr-components/pubsub.yaml` | CREATED | Pub/sub component CRD |
| `backend/src/utils/dapr/event_publisher.py` | CREATED (optional) | Event publishing utility |
| `backend/src/utils/dapr/state_manager.py` | CREATED (optional) | State management utility |
| `backend/src/api/events_router.py` | CREATED (optional) | Event subscription endpoints |

**Total**: 3 modified, 5 created (3 required infrastructure, 2 optional utilities)

---

**Plan Status**: ✅ COMPLETE - Ready for Task Generation (`/sp.tasks`)
