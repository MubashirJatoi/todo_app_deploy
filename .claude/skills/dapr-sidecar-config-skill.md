# Dapr Sidecar Config Skill

## Purpose
Configure Dapr sidecar runtime settings and behavior for specific applications.

## What it does
- Configures Dapr sidecar resource limits (CPU, memory)
- Sets Dapr runtime parameters (ports, protocols)
- Configures logging levels and formats
- Enables/disables specific Dapr features (metrics, tracing, mTLS)
- Sets up Dapr Configuration resources for advanced settings

## What it does NOT do
- Add Dapr annotations to deployments (use dapr-sidecar-annotation-skill)
- Create Dapr components
- Implement application code

## Usage
Use this skill when you need to:
- Tune Dapr sidecar performance settings
- Configure advanced Dapr runtime behavior
- Set up environment-specific Dapr configurations
- Optimize sidecar resource usage

## Example Configuration
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: appconfig
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin:9411/api/v2/spans"
  mtls:
    enabled: true
  metric:
    enabled: true
```