# Runbook: Dapr Operations for Todo Application

This runbook provides step-by-step instructions for common operational tasks related to the Dapr-enabled Todo application.

## Table of Contents
1. [Deployment Operations](#deployment-operations)
2. [Monitoring and Observability](#monitoring-and-observability)
3. [Troubleshooting](#troubleshooting)
4. [Scaling Operations](#scaling-operations)
5. [Backup and Recovery](#backup-and-recovery)
6. [Security Operations](#security-operations)

## Deployment Operations

### Deploy New Version with Dapr
```bash
# Update dependencies
helm dependency update

# Deploy with Dapr enabled
helm upgrade todo-app . \
  --install \
  --set dapr.enabled=true \
  --namespace default \
  --create-namespace
```

### Disable Dapr Temporarily
```bash
# Deploy without Dapr (for debugging)
helm upgrade todo-app . \
  --set dapr.enabled=false \
  --namespace default
```

### Rollback Dapr Deployment
```bash
# Rollback to previous version
helm rollback todo-app

# Or rollback to specific revision
helm rollback todo-app 2
```

## Monitoring and Observability

### Check Dapr Status
```bash
# Check Dapr control plane
dapr status -k

# Check Dapr sidecars
dapr list -k

# Check Dapr components
kubectl get components -n default
```

### Monitor Application Health
```bash
# Check pod status
kubectl get pods

# Check service status
kubectl get services

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd

# Check application logs
kubectl logs <pod-name>
```

### Performance Monitoring
```bash
# Check resource usage
kubectl top pods

# Check Dapr metrics
kubectl port-forward svc/dapr-dashboard 8080:8080
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Pods stuck in Init state
**Symptoms**: Pods show `Init:0/1` status
**Cause**: Dapr sidecar injection failed
**Solution**:
```bash
# Check if Dapr injector is running
kubectl get pods -n dapr-system

# Check Dapr system logs
kubectl logs -n dapr-system deployment/dapr-operator
kubectl logs -n dapr-system deployment/dapr-sidecar-injector

# Verify annotations in deployment
kubectl describe pod <pod-name>
```

#### Issue: Service invocation failing
**Symptoms**: Frontend can't reach backend via Dapr
**Cause**: Incorrect app-id or network issues
**Solution**:
```bash
# Verify app-ids
dapr list -k

# Test service invocation manually
kubectl port-forward <frontend-pod> 3500:3500
curl http://localhost:3500/v1.0/invoke/backend-app/method/health

# Check Dapr sidecar logs
kubectl logs <frontend-pod> -c daprd
kubectl logs <backend-pod> -c daprd
```

#### Issue: State store not working
**Symptoms**: State operations failing
**Cause**: Redis connectivity or configuration issues
**Solution**:
```bash
# Check Redis connectivity
kubectl exec -it <redis-pod> -- redis-cli ping

# Check state component status
kubectl describe component statestore

# Check Dapr logs for state errors
kubectl logs <backend-pod> -c daprd | grep state
```

#### Issue: Pub/Sub events not flowing
**Symptoms**: Events published but not received
**Cause**: Subscriber issues or Redis problems
**Solution**:
```bash
# Check pubsub component
kubectl describe component pubsub

# Verify subscription endpoint
kubectl logs <backend-pod> | grep "subscription"

# Test event publishing manually
kubectl exec -it <backend-pod> -- curl -X POST \
  http://localhost:3500/v1.0/publish/pubsub/task.created \
  -H "Content-Type: application/json" \
  -d '{"data": {"taskId": "123", "userId": "456"}}'
```

### Diagnostic Commands

#### Check Dapr Sidecar Injection
```bash
# Verify annotations exist
kubectl get deployment <app-name> -o yaml | grep dapr

# Check if sidecar is present
kubectl describe pod <pod-name> | grep daprd
```

#### Verify Component Configuration
```bash
# Check component definitions
kubectl get components -o yaml

# Validate component status
kubectl describe component <component-name>
```

#### Network Connectivity Tests
```bash
# Test service connectivity
kubectl exec -it <frontend-pod> -- curl -v http://localhost:3500/v1.0/healthz

# Test internal service resolution
kubectl exec -it <frontend-pod> -- nslookup backend-service
```

## Scaling Operations

### Scale Application Pods
```bash
# Scale frontend
kubectl scale deployment todo-app-frontend --replicas=3

# Scale backend
kubectl scale deployment todo-app-backend --replicas=3

# Check current replicas
kubectl get deployments
```

### Scale Redis (if needed)
```bash
# Scale Redis master (if using standalone)
kubectl scale statefulset todo-app-redis-master --replicas=1

# For Redis cluster, adjust values and upgrade
helm upgrade todo-app . --set redis.architecture=replication --set redis.replica.replicaCount=2
```

### Auto-scaling Configuration
```bash
# Check HPA status
kubectl get hpa

# Check scaling metrics
kubectl describe hpa <hpa-name>
```

## Backup and Recovery

### Dapr Component Backup
Dapr components are Kubernetes resources, so they're backed up with cluster backups.

### State Data Backup
Since we're using Redis for state, backup Redis data:
```bash
# Connect to Redis and create backup
kubectl exec -it <redis-pod> -- redis-cli BGSAVE

# Copy backup file
kubectl cp <namespace>/<redis-pod>:/data/dump.rdb ./redis-backup.rdb
```

### Recovery Procedures
```bash
# Restore Redis from backup
kubectl cp ./redis-backup.rdb <namespace>/<redis-pod>:/data/dump.rdb
kubectl exec -it <redis-pod> -- redis-cli BGREWRITEAOF
```

## Security Operations

### Rotate Redis Password
```bash
# Update Redis password
kubectl create secret generic redis-secret \
  --from-literal=password="new-secure-password" \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new password
kubectl rollout restart deployment/todo-app-backend
kubectl rollout restart deployment/todo-app-frontend
```

### Check Security Vulnerabilities
```bash
# Scan Dapr components
dapr dashboard

# Check for security advisories
dapr status -k
```

### Audit Dapr Operations
```bash
# Check Dapr audit logs
kubectl logs -n dapr-system deployment/dapr-placement-server

# Monitor for unauthorized access
kubectl logs <app-pod> -c daprd | grep -i denied
```

## Maintenance Tasks

### Regular Maintenance
```bash
# Clean up old pods
kubectl delete pods --field-selector=status.phase!=Running

# Check for deprecated API usage
kubectl get events --all-namespaces
```

### Dapr Runtime Updates
```bash
# Upgrade Dapr runtime
dapr upgrade -k

# Verify upgrade
dapr status -k
```

### Component Updates
```bash
# Update component configurations
kubectl apply -f <component-file>.yaml

# Restart pods to reload components
kubectl rollout restart deployment/todo-app-backend
```

## Emergency Procedures

### Immediate Response Steps
1. Assess scope of impact
2. Check Dapr system health: `dapr status -k`
3. Check application health: `kubectl get pods`
4. Review logs for error patterns
5. Isolate problematic components if possible

### Service Restoration
1. If Dapr is causing issues, temporarily disable: `helm upgrade --set dapr.enabled=false`
2. Restore basic functionality first
3. Investigate root cause
4. Re-enable Dapr once resolved

### Communication Template
```
Subject: Dapr-related Incident - Todo Application

Impact: [Describe impact on users/services]
Scope: [Affected components/users]
Timeline: [Start time, detection time, resolution time]
Root Cause: [Initial assessment]
Resolution: [Steps taken]
Next Steps: [Follow-up actions]
```

## Useful Commands Reference

### Quick Checks
```bash
# Overall health
kubectl get pods && dapr list -k

# Component status
kubectl get components && kubectl get services

# Recent events
kubectl get events --sort-by='.lastTimestamp'
```

### Debugging Shortcuts
```bash
# Tail logs from all app pods
kubectl get pods -o name | grep todo-app | xargs -I {} kubectl logs {} -f

# Check Dapr sidecar configs
kubectl get pods -o json | jq '.items[].spec.containers[] | select(.name=="daprd")'
```

This runbook should be updated regularly as new issues and solutions are discovered.