# Todo App Deployment to Kubernetes using Minikube and Helm

## Current Situation
- Docker images have been prepared (todo-backend:latest, todo-frontend:latest)
- Helm chart is available in ./charts/todo-app/
- Custom values file created: minikube-values.yaml
- Target environment: Minikube on D: drive due to C: drive space constraints

## Steps to Complete Deployment

### 1. Verify Docker is Running
Before proceeding, ensure Docker Desktop is running on your system.

### 2. Start Minikube with D: Drive Configuration
```bash
# Create directory on D: drive for Minikube
mkdir -p D:\minikube-data

# Set the MINIKUBE_HOME environment variable
set MINIKUBE_HOME=D:\minikube-data

# Start Minikube with minimal resources
minikube start --profile=tododeploy --driver=docker --memory=2048mb --cpus=2 --disk-size=4g
```

### 3. Configure Docker Environment for Minikube
```bash
# Set Docker environment to use Minikube's registry
@FOR /f "tokens=*" %i IN ('minikube docker-env --profile=tododeploy') DO @%i

# Verify images are available
docker images | findstr todo
```

### 4. Deploy Application Using Helm
```bash
# Install the application using Helm with custom values
helm install todo-app ./charts/todo-app/ -f minikube-values.yaml --create-namespace --namespace todo-app
```

### 5. Verify Deployment
```bash
# Check the status of deployed resources
kubectl get pods -n todo-app
kubectl get svc -n todo-app
kubectl get deployments -n todo-app
```

### 6. Access the Application
```bash
# Get the frontend service URL
minikube service frontend-svc -n todo-app --profile=tododeploy

# Or use tunnel for persistent access
minikube tunnel --profile=tododeploy
```

## Troubleshooting

### If Minikube won't start due to disk space:
1. Clear Docker cache: `docker system prune -af`
2. Stop unnecessary containers: `docker stop $(docker ps -aq)`
3. Use smaller disk allocation: `--disk-size=2g`

### If Helm deployment fails:
1. Check if Tiller/ Helm agent is running
2. Verify the Helm chart is valid: `helm lint ./charts/todo-app/`
3. Dry-run the installation: `helm install todo-app ./charts/todo-app/ -f minikube-values.yaml --dry-run`

## Expected Resources Created
- Namespaces: todo-app
- Deployments: frontend, backend, postgres
- Services: frontend-svc, backend-svc, postgres
- ConfigMaps and Secrets for application configuration
- PersistentVolumeClaims for database persistence