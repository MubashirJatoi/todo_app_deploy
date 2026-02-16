# Feature Specification: Cloud-Native Kubernetes Infrastructure for Todo Application

**Feature Branch**: `1-cloud-native`
**Created**: 2026-02-05
**Status**: Draft
**Input**: User description: "You are working under the Phase IV Constitution for the AI-Native Todo Application. The application is already fully implemented (Frontend, Backend, DB, AI Chatbot). Your task is to SPECIFY the exact infrastructure artifacts required to make this system Kubernetes-deployable on Minikube using Docker, Kubernetes, Helm, and AI Ops tools."

## Containerization Specification

### Dockerfile Requirements
- **Frontend Dockerfile** (frontend/Dockerfile): Multi-stage build for Next.js application with Node.js runtime
  - Build stage: Install dependencies and build Next.js app
  - Runtime stage: Copy build output to production image
  - Expose port 3000
  - Use non-root user for security
  - Copy .env files as ConfigMap volume mounts (not hardcoded)

- **Backend Dockerfile** (backend/Dockerfile): Multi-stage build for FastAPI application with Python runtime
  - Build stage: Install Python dependencies and prepare application
  - Runtime stage: Copy application files to production image
  - Expose port 8000
  - Use non-root user for security
  - Environment variables configured via Kubernetes Secrets/ConfigMaps

- **Build Context Strategy**: Separate build contexts for frontend and backend
  - Frontend: Context from frontend/ directory
  - Backend: Context from backend/ directory
  - Optimize Dockerfile with .dockerignore files to exclude unnecessary files

### Port Exposure Rules
- Frontend container: Expose port 3000 internally
- Backend container: Expose port 8000 internally
- No hardcoded port bindings in Dockerfiles
- Allow dynamic port configuration via environment variables

### Environment Variable Handling Strategy
- Convert all .env files to Kubernetes ConfigMaps and Secrets
- No environment variables hardcoded in Docker images
- Mount configuration via volume mounts or environment variable injection
- Sensitive data (secrets) managed exclusively through Kubernetes Secrets

## Kubernetes Resource Specification

### Deployments Required
- **frontend-deployment.yaml**: Kubernetes Deployment for frontend service
  - 2 replicas for high availability
  - Resource limits: CPU 500m, Memory 512Mi
  - Resource requests: CPU 100m, Memory 128Mi
  - Health checks: Liveness and readiness probes on port 3000
  - Security context: Run as non-root user

- **backend-deployment.yaml**: Kubernetes Deployment for backend service
  - 2 replicas for high availability
  - Resource limits: CPU 1000m, Memory 1Gi
  - Resource requests: CPU 200m, Memory 256Mi
  - Health checks: Liveness and readiness probes on port 8000
  - Security context: Run as non-root user

### Services Required
- **frontend-service.yaml**: NodePort Service for frontend access
  - Type: NodePort (for browser access in Minikube)
  - Port: 80 (external), TargetPort: 3000
  - NodePort range: 30000-32767 (default Minikube range)

- **backend-service.yaml**: ClusterIP Service for internal communication
  - Type: ClusterIP (internal access only)
  - Port: 8000, TargetPort: 8000
  - Selector matches backend deployment labels

### ConfigMaps Required
- **app-configmap.yaml**: Non-sensitive configuration
  - FRONTEND_API_URL: http://backend-service:8000 (internal service URL)
  - NEXT_PUBLIC_API_BASE_URL: http://frontend-service:80 (for inter-service communication)

### Secrets Required
- **app-secrets.yaml**: Sensitive configuration stored as Kubernetes Secrets
  - JWT_SECRET_KEY: Base64 encoded JWT signing key
  - DATABASE_URL: Base64 encoded Neon PostgreSQL connection string
  - BETTER_AUTH_SECRET: Base64 encoded Better Auth secret
  - BETTER_AUTH_URL: Base64 encoded auth callback URL

### Labels and Selectors Strategy
- **Common labels**: app.kubernetes.io/name: todo-app
- **Component labels**: app.kubernetes.io/component: frontend|backend|database
- **Version labels**: app.kubernetes.io/version: stable
- **Tier labels**: app.kubernetes.io/tier: frontend|backend|data
- **Selectors** must match deployment labels exactly for proper service discovery

## Networking & Service Exposure

### Internal Service Communication
- Frontend accesses backend via: http://backend-service:8000
- Backend accesses database via: internal Neon connection through secret
- DNS resolution: backend-service.default.svc.cluster.local (fully qualified)
- NetworkPolicy: Restrict traffic between services to only allowed paths

### External Access via NodePort
- Frontend service exposed as NodePort for browser access
- Access URL: http://MINIKUBE_IP:NODEPORT
- NodePort assigned dynamically in Minikube range (30000-32767)

### Internal DNS Naming Conventions
- Service names: frontend-service, backend-service, database-service
- DNS resolution: {service-name}.{namespace}.svc.cluster.local
- Internal communication uses service DNS names only

## Helm Chart Structure

### Helm Chart Layout
- **Chart.yaml**: Chart metadata including name, version, and description
- **values.yaml**: Default configuration values with configurable parameters
- **templates/**: Kubernetes resource templates with Helm templating
  - deployment-frontend.yaml
  - deployment-backend.yaml
  - service-frontend.yaml
  - service-backend.yaml
  - configmap-app.yaml
  - secret-app.yaml
  - NOTES.txt: Post-installation instructions

### values.yaml Structure
- replicaCount: Default 2 for both frontend and backend
- image: Container image repository and tag configuration
- service: NodePort configuration and ports
- resources: CPU/Memory limits and requests
- ingress: Ingress configuration (optional)
- secrets: Placeholder for sensitive values (empty by default)

### Template Parameterization Rules
- All configurable values use Helm templating ({{ .Values.parameter }})
- Secrets must use helm's tpl function for secure templating
- Conditional resources with if statements for optional features
- Namespaced resources with {{ .Release.Namespace }}

### Install Command Expectations
- Primary: `helm install todo-app ./charts/todo-app`
- With custom values: `helm install todo-app ./charts/todo-app -f custom-values.yaml`
- Uninstall: `helm uninstall todo-app`

## Minikube Deployment Specification

### Image Build Strategy for Minikube
- Use Minikube's built-in Docker daemon: `eval $(minikube docker-env)`
- Build images directly in Minikube's Docker environment
- Tag images as: todo-frontend:v1.0.0, todo-backend:v1.0.0
- No need to push to external registry (Minikube uses local images)

### Image Availability Inside Cluster
- Images built in Minikube Docker daemon are automatically available to cluster
- No registry configuration required for local development
- ImagePullPolicy: IfNotPresent (default) to use local images

### Deployment Order
1. Apply Secrets and ConfigMaps first
2. Deploy backend service with database connectivity
3. Deploy frontend service with backend service reference
4. Create services for network connectivity
5. Verify all deployments are ready

## AI Operations Specification

### kubectl-ai Inspection and Management
- All resources must have descriptive labels for AI recognition
- Standard annotations for metadata: version, owner, purpose
- Consistent naming conventions for resource discovery
- Health status properly reported through readiness/liveness probes

### kagent Monitoring Capabilities
- Pod annotations for kagent to recognize application topology
- Metrics endpoints properly exposed for kagent collection
- Health status reporting through standard Kubernetes status
- Log formatting compatible with kagent parsing

### AI-Operations Metadata Requirements
- All resources must include app.kubernetes.io/* standard labels
- Annotations for AI operations: ai/managed: "true", ai/type: "web-application"
- Proper namespace isolation with descriptive names
- Standard health check endpoints on all services

## Secrets & Configuration Management

### Conversion of .env to Kubernetes Secrets
- Parse all .env files from frontend and backend
- Convert sensitive values to base64 encoded strings
- Store in Kubernetes Secrets with descriptive names
- Map secrets to container environment variables or volumes

### Rules for Secret Mounting Into Pods
- Mount secrets as environment variables or volume mounts (not files)
- Secrets mounted with restrictive permissions (600 or 400)
- No secret data in container logs or stdout
- Automatic reloading when secrets change (optional via sidecar)

### No Plaintext Secrets in Manifests
- All secrets defined in separate Secret manifests
- Use Helm's tpl function for secure secret templating
- No secrets in ConfigMaps (only non-sensitive data)
- Pre-install hooks to validate secret presence

## Cloud-Native Blueprint Requirement

### Reusability for Similar Applications
- Generic naming conventions (replace app-specific names with templates)
- Parameterized configurations for different environments
- Modular templates that can be customized per application
- Documentation for adapting to new applications

### Generic Naming Conventions
- Use Helm template variables for application names
- Namespace parameterization for multi-tenant scenarios
- Component naming follows Kubernetes best practices
- No hardcoded application-specific names in templates

### Separation of App Logic from Infra Logic
- Infrastructure defines deployment, networking, and configuration
- Application code remains unchanged
- Configuration parameters externalized to values.yaml
- Environment-specific overrides in separate files

## Phase V Readiness

### Dapr Sidecar Addition Preparation
- Pod annotations for Dapr sidecar injection
- Named ports for Dapr service discovery
- Proper resource allocation accounting for Dapr overhead
- Sidecar configuration in deployment templates (conditional)

### Pod Annotations Strategy Placeholder
-预留 dapr.io/* annotations for future Dapr integration
-预留 istio.io/* annotations for future service mesh
-预留 prometheus.io/* annotations for monitoring
-预留 aiproxy/* annotations for AI proxy integration

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Full Application to Minikube (Priority: P1)

A DevOps engineer needs to deploy the existing full-stack todo application to a local Minikube cluster using a single Helm command. The engineer should be able to run a single install command and have all services (frontend, backend, database) running and communicating properly within the cluster.

**Why this priority**: This is the core value proposition of the cloud-native transformation - enabling simple deployment of the existing application to Kubernetes.

**Independent Test**: Can be fully tested by running `helm install todo-app ./todo-helm-chart` and verifying that all services are operational and accessible through the expected endpoints.

**Acceptance Scenarios**:

1. **Given** a fresh Minikube cluster, **When** the Helm chart is installed, **Then** frontend, backend, and database pods are running and healthy
2. **Given** the application is deployed, **When** user accesses the frontend via NodePort, **Then** they can interact with the todo application seamlessly

---

### User Story 2 - Manage Application with AI Operations Tools (Priority: P2)

An operations engineer needs to use AI-powered tools (kubectl-ai, kagent) to inspect, monitor, and manage the deployed application resources. The infrastructure must be properly labeled and annotated for AI tool recognition.

**Why this priority**: This enables the AI-operations aspect of the cloud-native blueprint, allowing for intelligent cluster management.

**Independent Test**: Can be tested by running kubectl-ai commands to inspect pods, services, and deployments, verifying that all resources are discoverable and manageable.

**Acceptance Scenarios**:

1. **Given** the application is deployed, **When** kubectl-ai inspects resources, **Then** all pods and services are discoverable with appropriate metadata
2. **Given** kagent is monitoring the cluster, **When** application pods are running, **Then** kagent can monitor their health and performance

---

### User Story 3 - Secure Configuration Management (Priority: P3)

A security engineer needs to ensure that all sensitive configuration (JWT secrets, database URLs, API keys) is securely managed using Kubernetes Secrets, with no plaintext secrets in manifests or containers.

**Why this priority**: This is critical for security compliance and proper cloud-native security practices.

**Independent Test**: Can be tested by inspecting Kubernetes resources and verifying that sensitive data is stored in Secrets and mounted appropriately, with no hardcoded values in container images or manifests.

**Acceptance Scenarios**:

1. **Given** the application is deployed, **When** Kubernetes resources are inspected, **Then** all sensitive data is stored in properly configured Secrets
2. **Given** the system configuration, **When** environment variables are reviewed, **Then** no plaintext secrets are exposed in container configurations

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST containerize the frontend and backend services separately into distinct Docker images
- **FR-002**: System MUST define Kubernetes Deployments for frontend and backend services with proper resource limits
- **FR-003**: System MUST expose frontend service to external traffic via NodePort for browser access
- **FR-004**: System MUST establish internal networking between frontend and backend within the cluster
- **FR-005**: System MUST create a Helm chart with templates for all required Kubernetes resources
- **FR-006**: System MUST manage sensitive configuration through Kubernetes Secrets with no plaintext values
- **FR-007**: System MUST define proper ConfigMaps for non-sensitive configuration data
- **FR-008**: System MUST implement proper labeling strategy for resource identification and management
- **FR-009**: System MUST be deployable via single `helm install` command to a Minikube cluster
- **FR-010**: System MUST provide AI-operations compatibility through proper annotations and metadata

### Key Entities *(include if feature involves data)*

- **Docker Image**: Containerized representation of frontend and backend services with proper build contexts and runtime configurations
- **Kubernetes Resource**: Deployments, Services, ConfigMaps, and Secrets that define the application infrastructure
- **Helm Chart**: Packaged collection of Kubernetes templates and configuration values for simplified deployment
- **Configuration Secret**: Encrypted storage of sensitive data (JWT secrets, database URLs, API keys) for secure access by application services

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can deploy the complete application to Minikube using a single `helm install` command in under 5 minutes
- **SC-002**: All application services (frontend, backend, database) are operational and communicating within 3 minutes of Helm installation
- **SC-003**: kubectl-ai can successfully inspect and manage all deployed resources with proper metadata and annotations
- **SC-004**: 100% of sensitive configuration data is stored in Kubernetes Secrets with no plaintext exposure
- **SC-005**: The cloud-native blueprint is reusable for similar full-stack applications with minimal customization required