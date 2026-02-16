# Dapr Helm Integration Skill

## Purpose
Integrate Dapr support into Helm charts for parameterized Kubernetes deployments.

## What it does
- Updates Helm templates to include Dapr annotations conditionally
- Creates Helm templates for Dapr components (state store, pub/sub)
- Parameterizes Dapr configuration in values.yaml
- Implements conditional Dapr enablement with feature flags
- Creates helper templates for Dapr annotation patterns

## What it does NOT do
- Create Helm charts from scratch
- Deploy or install Helm charts
- Configure individual Dapr components outside Helm

## Usage
Use this skill when you need to:
- Add Dapr support to existing Helm charts
- Parameterize Dapr settings for different environments
- Create reusable Dapr component templates
- Implement feature toggles for Dapr enablement

## Example values.yaml
```yaml
dapr:
  enabled: true
  logLevel: info
  enableMetrics: true

backend:
  dapr:
    appId: backend-app
    appPort: 8000
```

## Example Template Usage
```yaml
{{- if .Values.backend.dapr.enabled }}
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: {{ .Values.backend.dapr.appId | quote }}
  dapr.io/app-port: {{ .Values.backend.dapr.appPort | quote }}
{{- end }}
```
