# Dapr Observability Skill

## Purpose
Implement observability and debugging for Dapr-enabled applications using logs, metrics, and tracing.

## What it does
- Verifies Dapr sidecar injection status with `dapr list -k`
- Collects and analyzes Dapr sidecar logs
- Sets up distributed tracing with Zipkin/Jaeger
- Configures Prometheus metrics collection
- Creates Grafana dashboards for Dapr metrics
- Debugs Dapr component issues (state store, pub/sub failures)
- Monitors Dapr control plane health

## What it does NOT do
- Implement application business logic
- Deploy Dapr components or services
- Fix application code issues (only diagnoses Dapr-related problems)

## Usage
Use this skill when you need to:
- Verify Dapr sidecars are properly injected
- Debug service invocation or pub/sub failures
- Set up monitoring and alerting for Dapr apps
- Analyze distributed traces across microservices
- Troubleshoot Dapr component connectivity issues

## Key Commands
```bash
# Check Dapr control plane
dapr status -k

# List Dapr-enabled apps
dapr list -k

# View Dapr sidecar logs
kubectl logs <pod> -c daprd -f

# List Dapr components
kubectl get components -n default

# Test service invocation
dapr invoke -a backend-app -m /health -k
```

## Metrics to Monitor
```promql
# Request rate
rate(dapr_http_server_request_count[5m])

# Latency (p95)
histogram_quantile(0.95,
  rate(dapr_http_server_request_latencies_bucket[5m])
)

# Error rate
rate(dapr_http_server_request_count{status=~"5.."}[5m])
```

## Common Issues
- **Sidecar not injected**: Check `dapr status -k` and deployment annotations
- **Component connection failed**: Check component YAML and credentials
- **Service not found**: Verify app-id matches in both source and target
- **High latency**: Check sidecar resource limits and component performance
