# Quickstart Guide: Dapr Infrastructure Integration

This guide walks you through deploying the Todo application with Dapr capabilities enabled, transforming it into a distributed microservices architecture.

## Prerequisites

- Kubernetes cluster (Minikube, Kind, or cloud-based)
- Helm 3.x installed
- Dapr CLI installed and initialized on the cluster
- kubectl configured to access your cluster

## Step 1: Install Dapr on your Kubernetes Cluster

First, ensure Dapr is installed on your Kubernetes cluster:

```bash
# Initialize Dapr on the cluster (if not already done)
dapr init -k

# Verify Dapr is running
dapr status -k
```

Expected output should show Dapr control plane services running.

## Step 2: Prepare Redis for Dapr Components

Dapr state store and pub/sub components require a Redis instance. The Helm chart includes Redis as a subchart, but you'll need to create a Kubernetes secret for Redis authentication:

```bash
# Create Redis secret (adjust password as needed)
kubectl create secret generic redis-secret \
  --from-literal=password="redis-password-here" \
  --dry-run=client -o yaml | kubectl apply -f -
```

## Step 3: Deploy the Todo Application with Dapr Enabled

Navigate to the Helm chart directory and install the application with Dapr enabled:

```bash
# Navigate to the chart directory
cd charts/todo-app

# Update dependencies to fetch Redis chart
helm dependency update

# Install the application with Dapr enabled
helm install todo-app . \
  --set dapr.enabled=true \
  --set redis.auth.password="redis-password-here" \
  --namespace default \
  --create-namespace
```

## Step 4: Verify Dapr Integration

After deployment, verify that Dapr components are working correctly:

```bash
# Check that pods are running with 2 containers (app + daprd)
kubectl get pods

# Verify Dapr sidecars are registered
dapr list -k

# Check that Dapr components are created
kubectl get components

# View Dapr sidecar logs for initialization
kubectl logs <pod-name> -c daprd
```

You should see "dapr initialized. Status: Running" in the logs.

## Step 5: Test Application Functionality

Access the application and verify all functionality works as before:

```bash
# Port forward to access the frontend
kubectl port-forward svc/todo-app-frontend 3000:3000

# Or access the backend API
kubectl port-forward svc/todo-app-backend 8000:7860
```

## Step 6: Verify Dapr Features

### Service Invocation
Check that the frontend is using Dapr service invocation to communicate with the backend:

1. Set `NEXT_PUBLIC_DAPR_ENABLED=true` in frontend environment variables
2. Frontend requests should now route through `http://localhost:3500/v1.0/invoke/backend-app/method`

### Pub/Sub Events
Verify task events are being published and handled:

1. Create a task through the API
2. Check backend logs for "Received task.created event" messages
3. Events should flow through the pubsub component

### State Management
Verify state operations work with Dapr:

1. Use chat session functionality (if implemented)
2. State should be stored in Dapr state store with configured TTL

## Troubleshooting

### Common Issues

1. **Pods stuck in Pending state**: Check if Redis PVC is bound and resources are available
2. **Dapr sidecar not starting**: Verify Dapr control plane is running with `dapr status -k`
3. **Redis connection errors**: Ensure redis-secret contains correct password
4. **Service invocation failing**: Check that Dapr annotations are applied and app-id matches

### Useful Commands

```bash
# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd

# Check application logs
kubectl logs <pod-name>

# Verify Dapr components
kubectl describe component <component-name>

# Check Dapr placement service (for actors, if used)
kubectl logs -l app=dapr-placement-server -n dapr-system
```

## Scaling and Production Considerations

For production deployments, consider:

- Using a managed Redis service instead of in-cluster Redis
- Configuring TLS for Dapr components
- Setting up distributed tracing with Zipkin/Jaeger
- Implementing proper resource limits and HPA
- Securing Dapr components with mTLS