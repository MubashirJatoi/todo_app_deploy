# Tasks: Dapr Infrastructure Integration

**Input**: Design documents from `/specs/1-dapr-integration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this implementation as they were not explicitly requested in the feature specification. This is an infrastructure transformation focused on deployment and integration verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Web app structure: `backend/`, `frontend/`, `helm/todo-chart/`
- Helm templates: `helm/todo-chart/templates/`
- Dapr components: `helm/todo-chart/templates/dapr-components/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment preparation and prerequisite verification

- [ ] T001 Verify Dapr control plane status using `dapr status -k` command
- [ ] T002 Verify Kubernetes cluster access and default namespace availability
- [ ] T003 Create directory helm/todo-chart/templates/dapr-components/ for Dapr component YAMLs
- [ ] T004 [P] Update Helm dependencies to include Redis subchart in helm/todo-chart/Chart.yaml
- [ ] T005 [P] Run `helm dependency update` in helm/todo-chart directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Deploy Redis instance via Helm subchart or verify existing Redis deployment
- [ ] T007 Create Kubernetes Secret `redis-secret` with Redis password in default namespace
- [ ] T008 Verify Redis connectivity using kubectl exec and redis-cli ping command
- [ ] T009 Document Redis connection string `redis-master.default.svc.cluster.local:6379` in helm/todo-chart/values.yaml

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - DevOps Engineer Deploys Dapr-Enabled System (Priority: P1) 🎯 MVP

**Goal**: Deploy the entire todo application with Dapr capabilities enabled so that the system runs as a distributed microservices architecture without changing application code

**Independent Test**: Run `helm install todo-app ./helm/todo-chart` and verify each pod shows 2/2 containers (app + daprd sidecar) using `kubectl get pods` and `dapr list -k` shows all services

### Implementation for User Story 1

- [ ] T010 [P] [US1] Add dapr configuration section to helm/todo-chart/values.yaml with enabled, logLevel, enableMetrics flags
- [ ] T011 [P] [US1] Add frontend.dapr configuration with appId=frontend-app and appPort=3000 to helm/todo-chart/values.yaml
- [ ] T012 [P] [US1] Add backend.dapr configuration with appId=backend-app and appPort=8000 to helm/todo-chart/values.yaml
- [ ] T013 [P] [US1] Add stateStore configuration section to helm/todo-chart/values.yaml with type, redisHost, secretName, secretKey
- [ ] T014 [P] [US1] Add pubsub configuration section to helm/todo-chart/values.yaml with type, redisHost, secretName, secretKey
- [ ] T015 [US1] Create statestore component YAML in helm/todo-chart/templates/dapr-components/statestore.yaml with state.redis type
- [ ] T016 [US1] Create pubsub component YAML in helm/todo-chart/templates/dapr-components/pubsub.yaml with pubsub.redis type
- [ ] T017 [US1] Add conditional Dapr annotations to helm/todo-chart/templates/frontend-deployment.yaml with dapr.io/enabled, app-id, app-port, log-level
- [ ] T018 [US1] Add conditional Dapr annotations to helm/todo-chart/templates/backend-deployment.yaml with dapr.io/enabled, app-id, app-port, log-level, enable-metrics
- [ ] T019 [US1] Create Helm helper template for Dapr annotations in helm/todo-chart/templates/_helpers.tpl (optional, reduces duplication)
- [ ] T020 [US1] Validate Helm template rendering with `helm template todo-app ./helm/todo-chart --set dapr.enabled=true`
- [ ] T021 [US1] Run `helm lint ./helm/todo-chart` to validate chart structure and syntax
- [ ] T022 [US1] Deploy Helm chart with Dapr enabled using `helm install` or `helm upgrade` command
- [ ] T023 [US1] Wait for pods to reach 2/2 Ready state using `kubectl get pods -w` command
- [ ] T024 [US1] Verify Dapr sidecars registered with `dapr list -k` showing frontend-app and backend-app
- [ ] T025 [US1] Verify pod container count shows 2 containers (app + daprd) using `kubectl describe pod` command
- [ ] T026 [US1] Check Dapr sidecar logs for "dapr initialized. Status: Running" in daprd container logs
- [ ] T027 [US1] Verify Dapr components deployed with `kubectl get components -n default` showing statestore and pubsub
- [ ] T028 [US1] Test application functionality via port-forward to ensure no regression

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - Dapr sidecars running, components deployed, application accessible

---

## Phase 4: User Story 2 - System Architect Establishes Distributed Communication (Priority: P1)

**Goal**: Services communicate through Dapr service invocation instead of direct HTTP calls so that the system gains built-in resilience, service discovery, and distributed tracing

**Independent Test**: Call frontend API which invokes backend via Dapr, and verify through Dapr logs that invocation occurred (no direct HTTP call between pods)

### Implementation for User Story 2

- [ ] T029 [P] [US2] Identify direct HTTP calls between frontend and backend in frontend code
- [ ] T030 [US2] Replace frontend-to-backend HTTP calls with Dapr invocation URL format `http://localhost:3500/v1.0/invoke/backend-app/method/{endpoint}` in frontend service layer
- [ ] T031 [US2] Ensure HTTP headers (Authorization, correlation-id) are propagated through Dapr invocation calls
- [ ] T032 [US2] Add error handling for Dapr service invocation failures in frontend code
- [ ] T033 [US2] Deploy updated frontend service with Dapr invocation changes
- [ ] T034 [US2] Port-forward frontend pod Dapr sidecar port 3500 using `kubectl port-forward`
- [ ] T035 [US2] Test service invocation with `curl http://localhost:3500/v1.0/invoke/backend-app/method/health` command
- [ ] T036 [US2] Check Dapr sidecar logs for "invoking target backend-app" message in frontend daprd container
- [ ] T037 [US2] Verify backend receives requests through Dapr by checking backend application logs
- [ ] T038 [US2] Test frontend UI to ensure all backend API calls work through Dapr invocation

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - service invocation established, no direct pod-to-pod HTTP calls

---


## Phase 5: User Story 3 - Platform Engineer Enables Event-Driven Operations (Priority: P2)

**Goal**: Task operations (create, update, delete) publish events to pub/sub topics so that multiple services can react to task changes asynchronously without tight coupling

**Independent Test**: Create a task via API, verify event is published to `task.created` topic, and confirm subscriber receives the event via logs

### Implementation for User Story 3

- [ ] T039 [P] [US3] Add event publishing logic in backend after task creation in backend/src/routes/tasks.py or equivalent
- [ ] T040 [P] [US3] Add event publishing logic in backend after task update in backend/src/routes/tasks.py or equivalent
- [ ] T041 [P] [US3] Add event publishing logic in backend after task deletion in backend/src/routes/tasks.py or equivalent
- [ ] T042 [P] [US3] Add event publishing logic in backend after task completion in backend/src/routes/tasks.py or equivalent
- [ ] T043 [US3] Create CloudEvent helper function following CloudEvents 1.0 spec in backend/src/utils/events.py
- [ ] T044 [US3] Implement Dapr pub/sub publish using HTTP POST to `http://localhost:3500/v1.0/publish/pubsub/{topic}` in backend code
- [ ] T045 [US3] Create `/dapr/subscribe` endpoint in backend returning subscription configuration JSON
- [ ] T046 [US3] Create event handler endpoint `/events/task-created` in backend for task.created events
- [ ] T047 [US3] Create event handler endpoint `/events/task-updated` in backend for task.updated events
- [ ] T048 [US3] Create event handler endpoint `/events/task-deleted` in backend for task.deleted events
- [ ] T049 [US3] Create event handler endpoint `/events/task-completed` in backend for task.completed events
- [ ] T050 [US3] Implement activity logging in event handlers to record task events
- [ ] T051 [US3] Deploy updated backend service with pub/sub integration
- [ ] T052 [US3] Create a test task via API and verify `task.created` event published in Dapr logs
- [ ] T053 [US3] Verify subscriber receives event by checking `/events/task-created` endpoint logs
- [ ] T054 [US3] Update a task and verify `task.updated` event flows through pub/sub
- [ ] T055 [US3] Test event retry behavior by simulating subscriber failure

**Checkpoint**: All user stories 1-3 should now be independently functional - events flowing through pub/sub, activity logging working

---

## Phase 6: User Story 4 - Backend Developer Implements Distributed State Management (Priority: P3)

**Goal**: Store chat session history and temporary state in Dapr state store so that the system benefits from distributed caching and reduces database load for ephemeral data

**Independent Test**: Initiate a chatbot conversation, store session state via Dapr HTTP API, retrieve it later, and verify TTL expiration after configured time

### Implementation for User Story 4

- [ ] T056 [P] [US4] Create state management utility module in backend/src/utils/state.py with save/get/delete functions
- [ ] T057 [P] [US4] Implement save_state function using HTTP POST to `http://localhost:3500/v1.0/state/statestore` with TTL metadata
- [ ] T058 [P] [US4] Implement get_state function using HTTP GET from `http://localhost:3500/v1.0/state/statestore/{key}`
- [ ] T059 [P] [US4] Implement delete_state function using HTTP DELETE to `http://localhost:3500/v1.0/state/statestore/{key}`
- [ ] T060 [US4] Identify chat session storage points in backend chatbot code
- [ ] T061 [US4] Replace in-memory or database chat session storage with Dapr state store using key pattern `chat:session:{user_id}`
- [ ] T062 [US4] Add TTL metadata of 3600 seconds (1 hour) to chat session state entries
- [ ] T063 [US4] Implement user profile caching with key pattern `cache:user:{user_id}` and TTL of 1800 seconds
- [ ] T064 [US4] Implement task list caching with key pattern `cache:tasks:{user_id}` and TTL of 300 seconds
- [ ] T065 [US4] Deploy updated backend with state management integration
- [ ] T066 [US4] Test chat session storage by initiating conversation and verifying state in Redis
- [ ] T067 [US4] Test state retrieval by resuming chat session and verifying history loaded
- [ ] T068 [US4] Test TTL expiration by waiting 1 hour and verifying session state deleted
- [ ] T069 [US4] Test user profile caching performance improvement with before/after metrics

**Checkpoint**: All user stories 1-4 should now be independently functional - state management working, caching operational

---

## Phase 7: User Story 5 - SRE Monitors Distributed System Health (Priority: P3)

**Goal**: Verify Dapr sidecar status, inspect component health, and view distributed traces so that system operates correctly and troubleshooting is quick

**Independent Test**: Run `dapr list -k`, check component status via `kubectl get components`, and verify traces appear in Zipkin UI

### Implementation for User Story 5

- [ ] T070 [P] [US5] Create observability verification script in scripts/verify-dapr-health.sh
- [ ] T071 [P] [US5] Add `dapr list -k` command to health check script
- [ ] T072 [P] [US5] Add `kubectl get components -n default` command to health check script
- [ ] T073 [P] [US5] Add pod status verification with `kubectl get pods` to health check script
- [ ] T074 [P] [US5] Add Dapr sidecar log inspection commands to health check script
- [ ] T075 [US5] Deploy Zipkin for distributed tracing using `kubectl create deployment zipkin --image openzipkin/zipkin`
- [ ] T076 [US5] Expose Zipkin service with `kubectl expose deployment zipkin --type LoadBalancer --port 9411`
- [ ] T077 [US5] Create Dapr Configuration YAML in helm/todo-chart/templates/dapr-config.yaml with tracing enabled
- [ ] T078 [US5] Add dapr.io/config annotation to backend deployment referencing appconfig
- [ ] T079 [US5] Deploy updated configuration and restart pods to enable tracing
- [ ] T080 [US5] Make request through frontend to backend and verify trace appears in Zipkin UI
- [ ] T081 [US5] Run `dapr list -k` and verify all app-ids show healthy status within 5 seconds
- [ ] T082 [US5] Run `kubectl get components` and verify statestore and pubsub show CREATED status
- [ ] T083 [US5] Access Zipkin UI via `kubectl port-forward service/zipkin 9411:9411` and inspect traces
- [ ] T084 [US5] Measure service invocation latency and verify <50ms overhead compared to direct HTTP

**Checkpoint**: All user stories should now be independently functional - full observability operational

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T085 [P] Update quickstart.md with actual deployment commands and verification steps
- [ ] T086 [P] Add troubleshooting section to quickstart.md for common Dapr issues
- [ ] T087 [P] Create rollback procedures documentation in specs/1-dapr-integration/rollback.md
- [ ] T088 [P] Document performance benchmarks in specs/1-dapr-integration/performance.md
- [ ] T089 [P] Add Helm values examples for different environments in helm/todo-chart/examples/
- [ ] T090 Document distributed architecture blueprint in specs/1-dapr-integration/architecture.md
- [ ] T091 Run full quickstart.md validation end-to-end
- [ ] T092 Verify all 10 success criteria from spec.md are met
- [ ] T093 [P] Create runbook for common operational tasks in docs/runbooks/dapr-operations.md
- [ ] T094 [P] Add monitoring dashboards configuration for Dapr metrics
- [ ] T095 Performance testing with 1000 concurrent requests to validate throughput
- [ ] T096 Security review of component configurations and secret management
- [ ] T097 Final constitution compliance check against Phase V requirements

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T005) - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion (T006-T009)
  - User Story 1 (P1) can start after Foundational
  - User Story 2 (P1) can start after User Story 1 completion (T028)
  - User Story 3 (P2) can start after User Story 2 completion (T038)
  - User Story 4 (P3) can start after Foundational (independent of US2/US3)
  - User Story 5 (P3) can start after User Story 2 completion (needs service invocation working)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Dapr Deployment**: Can start after Foundational (Phase 2, T009) - No dependencies on other stories
- **User Story 2 (P1) - Service Invocation**: Depends on User Story 1 (T028) - Requires Dapr sidecars running
- **User Story 3 (P2) - Pub/Sub Events**: Depends on User Story 2 (T038) - Can leverage service invocation patterns
- **User Story 4 (P3) - State Management**: Can start after Foundational (T009) - Independent of US2/US3, only needs components from US1
- **User Story 5 (P3) - Observability**: Depends on User Story 2 (T038) - Needs operational system to observe

### Within Each User Story

**User Story 1** (Parallel opportunities):
- T010-T014 (values.yaml updates) can run in parallel
- T015-T016 (component YAMLs) can run in parallel after T010-T014
- T017-T018 (deployment annotations) can run in parallel after T010-T014

**User Story 2** (Sequential):
- T029 must complete before T030-T032
- T033 must complete before T034-T038

**User Story 3** (Parallel opportunities):
- T039-T042 (event publishing) can run in parallel
- T046-T049 (event handlers) can run in parallel after T043-T045

**User Story 4** (Parallel opportunities):
- T056-T059 (state utilities) can run in parallel
- T061-T064 (state implementation) can run after T060

**User Story 5** (Parallel opportunities):
- T070-T074 (health script) can run in parallel
- T075-T076 (Zipkin deployment) can run in parallel

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T004-T005)
- All Foundational tasks are sequential due to dependencies
- Within User Story 1: T010-T014, T015-T016, T017-T018 groups can parallelize
- Within User Story 3: T039-T042, T046-T049 groups can parallelize
- Within User Story 4: T056-T059, T061-T064 groups can parallelize
- Within User Story 5: T070-T074, T075-T076 groups can parallelize
- All Polish tasks marked [P] can run in parallel (T085-T089, T093-T094)

---

## Parallel Example: User Story 1

```bash
# Launch Helm values updates together:
Task T010: "Add dapr configuration section to helm/todo-chart/values.yaml"
Task T011: "Add frontend.dapr configuration to helm/todo-chart/values.yaml"
Task T012: "Add backend.dapr configuration to helm/todo-chart/values.yaml"
Task T013: "Add stateStore configuration to helm/todo-chart/values.yaml"
Task T014: "Add pubsub configuration to helm/todo-chart/values.yaml"

# Then launch component YAMLs together:
Task T015: "Create statestore.yaml in helm/todo-chart/templates/dapr-components/"
Task T016: "Create pubsub.yaml in helm/todo-chart/templates/dapr-components/"

# Then launch deployment annotations together:
Task T017: "Add Dapr annotations to helm/todo-chart/templates/frontend-deployment.yaml"
Task T018: "Add Dapr annotations to helm/todo-chart/templates/backend-deployment.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T009) - CRITICAL blocks all stories
3. Complete Phase 3: User Story 1 (T010-T028)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Verify 2/2 containers per pod
   - Verify `dapr list -k` shows apps
   - Verify components deployed
   - Verify application still functions
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T009)
2. Add User Story 1 → Test independently → Deploy/Demo (T010-T028) - MVP! Dapr infrastructure running
3. Add User Story 2 → Test independently → Deploy/Demo (T029-T038) - Service invocation working
4. Add User Story 3 → Test independently → Deploy/Demo (T039-T055) - Event-driven architecture operational
5. Add User Story 4 → Test independently → Deploy/Demo (T056-T069) - State management and caching active
6. Add User Story 5 → Test independently → Deploy/Demo (T070-T084) - Full observability enabled
7. Add Polish → Final validation (T085-T097) - Production ready
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T009)
2. Once Foundational is done (after T009):
   - Developer A: User Story 1 (T010-T028)
3. Once User Story 1 complete (after T028):
   - Developer B: User Story 2 (T029-T038)
   - Developer C: User Story 4 (T056-T069) - Can run in parallel with US2
4. Once User Story 2 complete (after T038):
   - Developer A: User Story 3 (T039-T055)
   - Developer D: User Story 5 (T070-T084) - Can run in parallel with US3
5. Stories complete and integrate independently

---

## Success Criteria Mapping

Each task maps to success criteria from spec.md:

- **SC-001** (2/2 containers): T023, T025
- **SC-002** (`dapr list -k` <5s): T024, T081
- **SC-003** (<50ms latency): T084
- **SC-004** (Components deployed): T027
- **SC-005** (Service invocation works): T035, T036
- **SC-006** (Events delivered <1s): T052, T053
- **SC-007** (State operations <100ms): T066, T067
- **SC-008** (1000 concurrent requests): T095
- **SC-009** (Helm install works): T022
- **SC-010** (100% functionality preserved): T028, T038, T091

---

## Notes

- [P] tasks = different files, no dependencies within that group
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Infrastructure-only transformation - no business logic changes
- All changes are Helm-managed and can be disabled with `dapr.enabled=false`
- Redis instance can be shared for both state store and pub/sub
- Follow key naming conventions strictly: `{domain}:{type}:{id}` for state, `{domain}.{entity}.{action}` for topics
