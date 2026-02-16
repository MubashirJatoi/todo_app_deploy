# Dapr Sidecar Annotation Skill

## Purpose
Add Dapr sidecar injection annotations to Kubernetes deployment manifests.

## What it does
- Adds required Dapr annotations to pod templates
- Configures app-id, app-port, and log-level
- Enables metrics and tracing via annotations
- Sets sidecar resource limits (CPU, memory)
- Configures Dapr runtime settings per application

## What it does NOT do
- Create or modify Kubernetes Deployments from scratch
- Configure Dapr components
- Implement application code changes

## Usage
Use this skill when you need to:
- Enable Dapr on existing Kubernetes deployments
- Add Dapr sidecar to new microservices
- Configure Dapr runtime settings for specific apps
- Enable metrics and tracing collection

## Essential Annotations
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend-app"
  dapr.io/app-port: "8000"
  dapr.io/log-level: "info"
  dapr.io/enable-metrics: "true"
  dapr.io/metrics-port: "9090"
```

## Example
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-app"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
```
