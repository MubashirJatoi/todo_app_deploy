# Todo App Helm Chart - Test Plan

This document outlines the comprehensive test plan for validating the full deployment workflow and all user stories.

## Test Environment Setup

### Prerequisites
- Kubernetes cluster (Minikube, Kind, or cloud-based)
- Helm 3.2.0+
- kubectl
- Optional: Dapr runtime, Istio control plane

### Test Configuration
```bash
# Clone or download the chart
git clone <repo-url>
cd charts/todo-app

# Create test values
cat <<EOF > test-values.yaml
# Test configuration with all features enabled
frontend:
  replicaCount: 1
  image:
    repository: nginx  # Using placeholder image for test
    tag: "alpine"
    pullPolicy: IfNotPresent

backend:
  replicaCount: 1
  image:
    repository: busybox  # Using placeholder image for test
    tag: "latest"
    pullPolicy: IfNotPresent

database:
  enabled: true
  image:
    repository: postgres
    tag: "15"

dapr:
  enabled: true
  logLevel: "info"

istio:
  enabled: false  # Enable if Istio is available

monitoring:
  enabled: true

namespace:
  create: true
  name: "todo-test"
EOF
```

## User Story Validation

### US1: User Registration and Authentication

#### Test Steps:
1. Deploy the chart with authentication enabled
2. Verify authentication service is accessible
3. Test user registration flow
4. Test login/logout functionality

#### Validation Commands:
```bash
# Check if all pods are running
kubectl get pods -n todo-test

# Verify authentication endpoints are accessible
kubectl port-forward -n todo-test svc/todo-app-backend 7860:7860 &
curl http://localhost:7860/health

# Check logs for authentication service
kubectl logs -n todo-test -l app.kubernetes.io/component=backend
```

### US2: Task Management Operations

#### Test Steps:
1. Verify task endpoints are available
2. Test CRUD operations for tasks
3. Validate task completion functionality
4. Test task deletion

#### Validation Commands:
```bash
# Check service endpoints
kubectl get svc -n todo-test

# Test API endpoints
kubectl port-forward -n todo-test svc/todo-app-backend 7860:7860 &
curl -X GET http://localhost:7860/api/tasks

# Check task service logs
kubectl logs -n todo-test -l app.kubernetes.io/component=backend
```

### US3: Personal Task Isolation

#### Test Steps:
1. Verify user data isolation mechanisms
2. Test that users can only access their own tasks
3. Validate security controls

#### Validation Commands:
```bash
# Check database connectivity and isolation
kubectl exec -n todo-test -it deployment/todo-app-database -- psql -U user -d todo_db -c "\dt"

# Verify security context settings
kubectl describe -n todo-test deployment/todo-app-backend
kubectl describe -n todo-test deployment/todo-app-frontend
```

## Feature-Specific Tests

### Dapr Integration Test
```bash
# Check if Dapr sidecars are injected
kubectl get pods -n todo-test -o jsonpath='{range .items[*]}{@.metadata.name}{"\t"}{len @.spec.containers}{"\n"}{end}'

# Verify Dapr annotations are present
kubectl describe -n todo-test deployment/todo-app-backend | grep dapr
kubectl describe -n todo-test deployment/todo-app-frontend | grep dapr
```

### Monitoring Test
```bash
# Check if monitoring annotations are present
kubectl describe -n todo-test deployment/todo-app-backend | grep prometheus
kubectl describe -n todo-test deployment/todo-app-frontend | grep prometheus

# Verify ServiceMonitors are created
kubectl get servicemonitor -n todo-test
```

### Security Test
```bash
# Verify non-root user execution
kubectl describe -n todo-test deployment/todo-app-backend | grep "Run As Non Root"
kubectl describe -n todo-test deployment/todo-app-frontend | grep "Run As Non Root"

# Check secret management
kubectl get secrets -n todo-test
kubectl describe secret -n todo-test todo-app-auth-secret
```

## Resource Validation Tests

### Resource Limits and Requests
```bash
# Verify resource limits are applied
kubectl describe -n todo-test deployment/todo-app-backend | grep -A 5 Resources
kubectl describe -n todo-test deployment/todo-app-frontend | grep -A 5 Resources
```

### Service Discovery
```bash
# Verify services are created and accessible
kubectl get svc -n todo-test
kubectl describe svc -n todo-test todo-app-frontend
kubectl describe svc -n todo-test todo-app-backend
```

## Health and Readiness Tests

### Health Checks
```bash
# Check pod health status
kubectl get pods -n todo-test -o wide

# Verify health check endpoints
kubectl describe -n todo-test deployment/todo-app-backend | grep -A 10 Liveness
kubectl describe -n todo-test deployment/todo-app-frontend | grep -A 10 Liveness
```

### Readiness Checks
```bash
# Verify readiness probes
kubectl describe -n todo-test deployment/todo-app-backend | grep -A 10 Readiness
kubectl describe -n todo-test deployment/todo-app-frontend | grep -A 10 Readiness
```

## AI Operations Validation

### AI Annotations and Labels
```bash
# Verify AI-related annotations
kubectl get pods -n todo-test -o jsonpath='{.items[*].metadata.annotations}' | grep ai

# Check AI-discoverable labels
kubectl get all,cm,secret -n todo-test -l ai/discoverable=true
```

## Cleanup Test

### Uninstallation
```bash
# Test clean uninstallation
helm uninstall todo-app -n todo-test

# Verify all resources are removed
kubectl get all,cm,secret,ingress,pvc -n todo-test

# Clean up namespace if created
kubectl delete namespace todo-test
```

## Performance Tests (Optional)

### Resource Utilization
```bash
# Monitor resource usage
kubectl top pods -n todo-test

# Check if resource limits are respected
kubectl describe nodes
```

## Expected Results

### Success Criteria
- All pods start successfully and reach Running state
- All services are accessible
- Health checks pass
- Dapr sidecars are injected when enabled
- Monitoring annotations are present
- Security contexts are properly configured
- Resource limits are enforced
- AI annotations and labels are applied
- All user stories are functionally validated

### Failure Indicators
- Pods stuck in Pending, CrashLoopBackOff, or Error state
- Services inaccessible
- Failed health checks
- Missing security configurations
- Resource limits not applied

## Automated Test Script

```bash
#!/bin/bash
# Automated validation script

NAMESPACE="todo-test"
RELEASE_NAME="todo-app"

echo "Starting comprehensive validation of $RELEASE_NAME..."

# Wait for all pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=Ready pods --all -n $NAMESPACE --timeout=300s

# Validate deployments
echo "Validating deployments..."
kubectl get deployments -n $NAMESPACE
kubectl rollout status deployment/todo-app-frontend -n $NAMESPACE
kubectl rollout status deployment/todo-app-backend -n $NAMESPACE

# Validate services
echo "Validating services..."
kubectl get svc -n $NAMESPACE

# Validate secrets
echo "Validating secrets..."
kubectl get secrets -n $NAMESPACE | grep todo-app

# Validate configmaps
echo "Validating configmaps..."
kubectl get configmaps -n $NAMESPACE | grep todo-app

# Validate Dapr if enabled
if kubectl get deployment todo-app-backend -n $NAMESPACE -o yaml | grep -q "dapr.io/enabled"; then
    echo "Dapr annotations found"
else
    echo "WARNING: Dapr annotations not found"
fi

# Validate monitoring if enabled
if kubectl get deployment todo-app-backend -n $NAMESPACE -o yaml | grep -q "prometheus.io/scrape"; then
    echo "Monitoring annotations found"
else
    echo "WARNING: Monitoring annotations not found"
fi

# Validate AI annotations
if kubectl get deployment todo-app-backend -n $NAMESPACE -o yaml | grep -q "ai/managed"; then
    echo "AI annotations found"
else
    echo "WARNING: AI annotations not found"
fi

echo "Validation completed. Check for any warnings above."
```

## Post-Deployment Verification Checklist

- [ ] All deployments are healthy and scaled to expected replica count
- [ ] All services are accessible and routing correctly
- [ ] Secrets are properly configured and accessible to pods
- [ ] ConfigMaps contain expected configuration values
- [ ] Resource limits and requests are properly set
- [ ] Security contexts are applied correctly
- [ ] Health and readiness probes are configured
- [ ] Dapr sidecars are injected when enabled
- [ ] Monitoring annotations are present
- [ ] AI-related labels and annotations are applied
- [ ] Network connectivity between components works
- [ ] Persistence is configured for the database
- [ ] All user stories are functionally validated