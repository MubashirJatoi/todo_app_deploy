# Distributed Configuration Skill

## Purpose
Manage configuration for distributed microservices using Kubernetes ConfigMaps, Secrets, and environment variables.

## What it does
- Defines environment-specific configuration (dev, staging, prod)
- Creates Kubernetes ConfigMaps for non-sensitive config
- Creates Kubernetes Secrets for sensitive data (passwords, API keys)
- Implements configuration injection via environment variables
- Documents configuration dependencies per service
- Handles configuration updates and reloads

## What it does NOT do
- Implement application logic that uses configuration
- Deploy or manage Kubernetes resources directly
- Handle runtime configuration changes (requires restart)

## Usage
Use this skill when you need to:
- Externalize configuration from application code
- Manage different configurations per environment
- Secure sensitive credentials using Kubernetes Secrets
- Share common configuration across multiple services
- Document required configuration for each microservice

## Example ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-config
data:
  DAPR_HTTP_PORT: "3500"
  DAPR_GRPC_PORT: "50001"
  LOG_LEVEL: "info"
  PUBSUB_NAME: "pubsub"
  STATE_STORE_NAME: "statestore"
```

## Example Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:pass@host:5432/db"
  REDIS_PASSWORD: "secret123"
  JWT_SECRET_KEY: "super-secret-key"
```

## Example Usage in Deployment
```yaml
spec:
  containers:
  - name: backend
    envFrom:
    - configMapRef:
        name: todo-config
    env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: todo-secrets
          key: DATABASE_URL
```
