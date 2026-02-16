# Rollback Procedures: Dapr Infrastructure Integration

This document outlines the procedures for rolling back the Dapr integration if issues arise after deployment.

## Overview

The Dapr integration introduces several infrastructure components that can be rolled back independently or as a whole. This document provides step-by-step procedures for various rollback scenarios.

## Rollback Scenarios

### Scenario 1: Complete Rollback (Disable Dapr Entirely)

If critical issues require complete removal of Dapr integration:

1. **Scale down application deployments**:
   ```bash
   kubectl scale deployment todo-app-frontend --replicas=0
   kubectl scale deployment todo-app-backend --replicas=0
   ```

2. **Remove Dapr annotations from deployments**:
   - Set `dapr.enabled=false` in values.yaml
   - Redeploy without Dapr sidecars:
   ```bash
   helm upgrade todo-app . --set dapr.enabled=false
   ```

3. **Update frontend to use direct API calls**:
   - Set `NEXT_PUBLIC_DAPR_ENABLED=false` in frontend environment
   - Redeploy frontend with direct API calls

4. **Scale up application deployments**:
   ```bash
   kubectl scale deployment todo-app-frontend --replicas=1
   kubectl scale deployment todo-app-backend --replicas=1
   ```

### Scenario 2: Disable Specific Dapr Components

#### Disable Pub/Sub Events
1. Comment out or remove event publishing code in backend
2. Remove event handler endpoints from main.py
3. Remove pubsub component from Helm templates
4. Redeploy backend without pub/sub functionality

#### Disable State Management
1. Comment out or remove Dapr state store usage in backend
2. Revert to original state management approach
3. Remove statestore component from Helm templates
4. Redeploy backend without Dapr state management

#### Disable Service Invocation
1. Update frontend to use direct API calls instead of Dapr invocation
2. Remove Dapr annotations from frontend deployment
3. Redeploy frontend with direct API calls

### Scenario 3: Component-Level Rollback

#### Rollback Redis Component
If Redis issues occur:
1. Scale down Redis StatefulSet:
   ```bash
   kubectl scale statefulset todo-app-redis-master --replicas=0
   ```
2. Temporarily disable Redis-dependent features
3. Investigate and fix the issue
4. Scale back up when resolved

#### Rollback Dapr Sidecars
If sidecar issues occur:
1. Remove Dapr annotations from problematic deployments
2. Restart deployments to remove sidecars:
   ```bash
   kubectl rollout restart deployment/<deployment-name>
   ```

## Pre-Rollback Checklist

Before performing any rollback:

- [ ] Notify stakeholders of planned rollback
- [ ] Ensure backup of critical data
- [ ] Document current state and any error conditions
- [ ] Schedule maintenance window if needed
- [ ] Prepare rollback scripts/commands
- [ ] Have team members available for monitoring

## Rollback Execution Steps

### 1. Immediate Actions
- Stop traffic to affected services if possible
- Document current state (`kubectl get pods`, `dapr list -k`, etc.)
- Capture logs from problematic components

### 2. Execute Rollback
Follow the appropriate scenario procedure above

### 3. Verification
- Confirm services are operational
- Verify application functionality
- Check logs for errors
- Test critical user flows

### 4. Post-Rollback Actions
- Monitor system for stability
- Document what went wrong and why rollback was needed
- Plan permanent fix for the underlying issue
- Update procedures if needed

## Rollback Commands Reference

### Check Current State
```bash
# Check Dapr sidecars
dapr list -k

# Check pods
kubectl get pods

# Check Dapr components
kubectl get components

# Check application logs
kubectl logs <pod-name>
kubectl logs <pod-name> -c daprd
```

### Helm-Based Rollback
```bash
# Rollback to previous release
helm rollback todo-app

# Or reinstall without Dapr
helm uninstall todo-app
helm install todo-app . --set dapr.enabled=false
```

### Emergency Manual Rollback
```bash
# If Helm is unavailable, manually edit deployments
kubectl patch deployment todo-app-backend -p '{"spec":{"template":{"metadata":{"annotations":{"dapr.io/enabled":"false"}}}}}'
kubectl patch deployment todo-app-frontend -p '{"spec":{"template":{"metadata":{"annotations":{"dapr.io/enabled":"false"}}}}}'
```

## Rollback Timeline Expectations

- Minor component rollback: 5-15 minutes
- Service-level rollback: 15-30 minutes
- Complete rollback: 30-60 minutes
- Full redeployment: 60+ minutes

## Contact Information

For assistance during rollback:
- Platform Team: [contact information]
- DevOps Team: [contact information]
- On-call Engineer: [contact information]

## Post-Rollback Analysis

After any rollback, conduct a post-mortem including:
- Root cause analysis
- Timeline of events
- Impact assessment
- Lessons learned
- Prevention measures
- Updated procedures