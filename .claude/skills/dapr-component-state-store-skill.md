# Dapr Component State Store Skill

## Purpose
Define and create Dapr state store component YAML manifests for distributed state management.

## What it does
- Creates state store component YAML files (Redis, PostgreSQL, MongoDB)
- Configures connection strings and authentication using Kubernetes secrets
- Sets up TTL, consistency, and concurrency settings
- Defines component scopes to control app access
- Integrates with Kubernetes namespaces and RBAC

## What it does NOT do
- Implement application logic for state operations
- Install or manage the underlying state store infrastructure (Redis, PostgreSQL)
- Handle application-level caching strategies

## Usage
Use this skill when you need to:
- Create a new state store component for Dapr apps
- Configure state store metadata and connection parameters
- Set up multi-tier state storage (Redis for cache, PostgreSQL for persistence)
- Restrict state store access to specific applications

## Example
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis-master:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis-secret
      key: password
  scopes:
  - backend-app
```
