# Data Model for Cloud-Native Infrastructure

## Kubernetes Resource Entities

### Docker Image
- **Name**: Containerized representation of application service
- **Fields**: repository, tag, build_context, security_context
- **Relationships**: Deployments use Images as their source

### Kubernetes Deployment
- **Name**: Application workload controller
- **Fields**: replicas, resource_limits, health_checks, security_context
- **Relationships**: Deployments create Pods, reference Services

### Kubernetes Service
- **Name**: Network access point for application
- **Fields**: type (NodePort/ClusterIP), ports, selectors, dns_name
- **Relationships**: Services route to Deployments via selectors

### Kubernetes ConfigMap
- **Name**: Non-sensitive configuration storage
- **Fields**: key_value_pairs, mount_paths, environment_variables
- **Relationships**: Referenced by Deployments for configuration

### Kubernetes Secret
- **Name**: Sensitive data storage
- **Fields**: base64_encoded_data, mount_paths, environment_variables
- **Relationships**: Referenced by Deployments for sensitive configuration

### Helm Chart
- **Name**: Packaged Kubernetes application
- **Fields**: metadata, templates, values, dependencies
- **Relationships**: Contains multiple Kubernetes resources as templates

## Validation Rules
- All Deployments must have proper resource limits
- All sensitive data must be stored in Secrets
- All Services must have proper selectors matching Deployments
- All ConfigMaps and Secrets must be referenced by Deployments
- All resources must follow proper labeling strategy

## State Transitions
- Helm Chart: Draft → Validated → Installed → Upgraded → Deleted
- Deployment: Created → Running → Scaling → Updating → Terminated
- Pod: Pending → Running → Succeeded → Failed → Unknown