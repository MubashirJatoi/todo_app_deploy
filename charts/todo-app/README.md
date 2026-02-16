# Todo App Helm Chart

This Helm chart deploys a full-stack Todo application with Next.js frontend, FastAPI backend, and PostgreSQL database. The chart includes support for Dapr, service mesh, monitoring, and AI operations.

## Chart Information

- **Chart Name:** todo-app
- **Version:** 1.0.0
- **App Version:** 1.0.0
- **Maintainer:** Todo App Team
- **Description:** A production-ready Helm chart for deploying the Todo application with advanced features

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PV provisioner support in the underlying infrastructure (for database persistence)

## Installing the Chart

To install the chart with the release name `todo-app`:

```bash
# Add any required repositories
helm repo add bitnami https://charts.bitnami.com/bitnami

# Install the chart with default values
helm install todo-app .

# Install with custom values
helm install todo-app . -f my-values.yaml
```

## Upgrading the Chart

```bash
# Upgrade to the latest version
helm upgrade todo-app .

# Rollback to a previous release
helm rollback todo-app [RELEASE_NUMBER]
```

## Uninstalling the Chart

```bash
# Uninstall the release
helm uninstall todo-app
```

## Configuration

The following table lists the configurable parameters of the todo-app chart and their default values.

### Frontend Configuration

| Parameter                          | Description                                                      | Default                               |
| ---------------------------------- | ---------------------------------------------------------------- | ------------------------------------- |
| `frontend.enabled`                 | Enable frontend deployment                                       | `true`                                |
| `frontend.replicaCount`            | Number of frontend pods                                          | `1`                                   |
| `frontend.image.repository`        | Frontend image repository                                        | `todo-frontend`                       |
| `frontend.image.pullPolicy`        | Frontend image pull policy                                       | `IfNotPresent`                        |
| `frontend.image.tag`               | Frontend image tag                                               | `""` (defaults to appVersion)         |
| `frontend.service.type`            | Frontend service type                                            | `NodePort`                            |
| `frontend.service.port`            | Frontend service port                                            | `3000`                                |
| `frontend.service.targetPort`      | Frontend service target port                                     | `3000`                                |
| `frontend.resources.limits.cpu`    | Frontend CPU limit                                               | `500m`                                |
| `frontend.resources.limits.memory` | Frontend memory limit                                            | `512Mi`                               |
| `frontend.resources.requests.cpu`  | Frontend CPU request                                             | `100m`                                |
| `frontend.resources.requests.memory`| Frontend memory request                                           | `128Mi`                               |

### Backend Configuration

| Parameter                         | Description                                                     | Default                               |
| --------------------------------- | --------------------------------------------------------------- | ------------------------------------- |
| `backend.enabled`                 | Enable backend deployment                                       | `true`                                |
| `backend.replicaCount`            | Number of backend pods                                          | `1`                                   |
| `backend.image.repository`        | Backend image repository                                        | `todo-backend`                        |
| `backend.image.pullPolicy`        | Backend image pull policy                                       | `IfNotPresent`                        |
| `backend.image.tag`               | Backend image tag                                               | `""` (defaults to appVersion)         |
| `backend.service.type`            | Backend service type                                            | `ClusterIP`                           |
| `backend.service.port`            | Backend service port                                            | `7860`                                |
| `backend.service.targetPort`      | Backend service target port                                     | `7860`                                |
| `backend.resources.limits.cpu`    | Backend CPU limit                                               | `1000m`                               |
| `backend.resources.limits.memory` | Backend memory limit                                            | `1Gi`                                 |
| `backend.resources.requests.cpu`  | Backend CPU request                                             | `250m`                                |
| `backend.resources.requests.memory`| Backend memory request                                           | `256Mi`                               |

### Database Configuration

| Parameter                         | Description                                                     | Default                               |
| --------------------------------- | --------------------------------------------------------------- | ------------------------------------- |
| `database.enabled`                | Enable database deployment                                      | `true`                                |
| `database.image.repository`       | Database image repository                                       | `postgres`                            |
| `database.image.tag`              | Database image tag                                              | `"15"`                                |
| `database.service.port`           | Database service port                                           | `5432`                                |
| `database.volume.enabled`         | Enable persistent volume for database                           | `true`                                |
| `database.volume.size`            | Database volume size                                            | `1Gi`                                 |
| `database.resources.limits.cpu`   | Database CPU limit                                              | `300m`                                |
| `database.resources.limits.memory`| Database memory limit                                           | `256Mi`                               |

### Dapr Configuration

| Parameter                         | Description                                                     | Default                               |
| --------------------------------- | --------------------------------------------------------------- | ------------------------------------- |
| `dapr.enabled`                    | Enable Dapr sidecar injection                                 | `false`                               |
| `dapr.httpPort`                   | Dapr HTTP port                                                  | `3500`                                |
| `dapr.grpcPort`                   | Dapr gRPC port                                                  | `50001`                               |
| `dapr.appProtocol`                | Application protocol (http/grpc)                               | `http`                                |
| `dapr.logLevel`                   | Dapr sidecar log level                                          | `info`                                |

### Istio Configuration

| Parameter                         | Description                                                     | Default                               |
| --------------------------------- | --------------------------------------------------------------- | ------------------------------------- |
| `istio.enabled`                   | Enable Istio sidecar injection                                  | `false`                               |
| `istio.controlPlane`              | Istio control plane revision                                    | `""`                                  |
| `istio.injectionPolicy`           | Istio injection policy                                          | `""`                                  |

### Monitoring Configuration

| Parameter                         | Description                                                     | Default                               |
| --------------------------------- | --------------------------------------------------------------- | ------------------------------------- |
| `monitoring.enabled`              | Enable monitoring                                               | `true`                                |
| `monitoring.metricsPath`          | Metrics endpoint path                                           | `/metrics`                            |

### Namespace Configuration

| Parameter                         | Description                                                     | Default                               |
| --------------------------------- | --------------------------------------------------------------- | ------------------------------------- |
| `namespace.create`                | Create namespace if it doesn't exist                           | `false`                               |
| `namespace.name`                  | Namespace name for all resources                                | `""`                                  |

### Minikube Configuration

| Parameter                         | Description                                                     | Default                               |
| --------------------------------- | --------------------------------------------------------------- | ------------------------------------- |
| `minikube.enabled`                | Enable Minikube-specific configuration                          | `false`                               |
| `minikube.imagePullPolicy`        | Image pull policy for Minikube                                  | `IfNotPresent`                        |
| `minikube.serviceType`            | Service type for Minikube                                       | `NodePort`                            |

## Advanced Features

### Dapr Integration
The chart supports Dapr sidecar injection for building distributed applications. Enable it by setting `dapr.enabled=true` in your values file.

### Service Mesh
Istio integration is available by setting `istio.enabled=true` in your values file.

### Monitoring
Prometheus-compatible metrics are enabled by default. ServiceMonitors are included for scraping metrics.

### AI Operations
AI-related labels and annotations are included for enhanced resource discovery and management.

### Security
- All deployments run with non-root users
- Proper RBAC is configured
- Secrets are properly managed
- Network policies can be configured separately

## Example Usage

### Production Deployment
```yaml
# production-values.yaml
frontend:
  replicaCount: 3
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi
  service:
    type: LoadBalancer

backend:
  replicaCount: 3
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi

database:
  volume:
    size: 10Gi

dapr:
  enabled: true
  logLevel: "warn"

monitoring:
  enabled: true
```

### Development Deployment
```yaml
# development-values.yaml
frontend:
  replicaCount: 1
  image:
    pullPolicy: Always
    tag: "dev-latest"

backend:
  replicaCount: 1
  image:
    pullPolicy: Always
    tag: "dev-latest"

database:
  volume:
    enabled: false  # Use ephemeral storage for dev

minikube:
  enabled: true
  resourceLimits:
    frontend:
      cpu: 300m
      memory: 256Mi
    backend:
      cpu: 500m
      memory: 512Mi
```

## Troubleshooting

### Common Issues

1. **Pods stuck in Pending state**: Check if there's sufficient resources in the cluster and PVs are available
2. **Service unavailable**: Verify service type and node ports if using NodePort
3. **Database connection failures**: Check if the database pod is running and secrets are properly configured

### Debugging

```bash
# Check pod status
kubectl get pods

# Check pod logs
kubectl logs -l app.kubernetes.io/name=todo-app

# Describe pod for detailed information
kubectl describe pod [pod-name]

# Check services
kubectl get svc

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

## Contributing

Please refer to the project documentation for contribution guidelines.

## License

Apache 2.0

## Installing with Minikube-specific Configuration

```bash
# Create a values file for minikube
cat <<EOF > minikube-values.yaml
minikube:
  resourceLimits:
    frontend:
      cpu: 300m
      memory: 256Mi
    backend:
      cpu: 500m
      memory: 512Mi
    database:
      cpu: 300m
      memory: 256Mi
  databaseVolume:
    size: 512Mi

frontend:
  service:
    type: NodePort

ingress:
  enabled: false
EOF

# Install with minikube configuration
helm install todo-app -f minikube-values.yaml .
```

## Configuration

The following table lists the configurable parameters of the todo-app chart and their default values.

| Parameter                          | Description                                                      | Default                               |
| ---------------------------------- | ---------------------------------------------------------------- | ------------------------------------- |
| `frontend.enabled`                 | Enable frontend deployment                                       | `true`                                |
| `frontend.replicaCount`            | Number of frontend pods                                          | `1`                                   |
| `frontend.image.repository`        | Frontend image repository                                        | `todo-frontend`                       |
| `frontend.image.pullPolicy`        | Frontend image pull policy                                       | `IfNotPresent`                        |
| `frontend.image.tag`               | Frontend image tag                                               | `""` (defaults to appVersion)         |
| `frontend.service.type`            | Frontend service type                                            | `NodePort`                            |
| `frontend.service.port`            | Frontend service port                                            | `3000`                                |
| `frontend.resources.limits.cpu`    | Frontend CPU limit                                               | `500m`                                |
| `frontend.resources.limits.memory` | Frontend memory limit                                            | `512Mi`                               |
| `backend.enabled`                  | Enable backend deployment                                        | `true`                                |
| `backend.replicaCount`             | Number of backend pods                                           | `1`                                   |
| `backend.image.repository`         | Backend image repository                                         | `todo-backend`                        |
| `backend.image.pullPolicy`         | Backend image pull policy                                        | `IfNotPresent`                        |
| `backend.image.tag`                | Backend image tag                                                | `""` (defaults to appVersion)         |
| `backend.service.type`             | Backend service type                                             | `ClusterIP`                           |
| `backend.service.port`             | Backend service port                                             | `7860`                                |
| `database.enabled`                 | Enable database deployment                                       | `true`                                |
| `database.image.repository`        | Database image repository                                        | `postgres`                            |
| `database.image.tag`               | Database image tag                                               | `"15"`                                |
| `database.volume.enabled`          | Enable persistent volume for database                            | `true`                                |
| `database.volume.size`             | Database volume size                                             | `1Gi`                                 |
| `ingress.enabled`                  | Enable ingress resource                                          | `false`                               |
| `ingress.className`                | Ingress class name                                               | `""`                                  |
| `ingress.hosts[0].host`            | Hostname for the ingress                                         | `chart-example.local`                 |
| `ingress.hosts[0].paths[0].path`   | Path for the ingress                                             | `/`                                   |

## Uninstalling the Chart

To uninstall/delete the `todo-app` release:

```bash
helm delete todo-app
```

## Minikube Deployment

For Minikube deployment, use the smaller resource limits as shown in the minikube-values.yaml example above.

After installation, you can access the frontend using the NodePort:

```bash
# Get the frontend service details
kubectl get svc todo-app-frontend

# Access the application
minikube service todo-app-frontend --url
```