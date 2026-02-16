# Quickstart Guide: Cloud-Native Todo Application

## Prerequisites
- Docker
- Minikube
- kubectl
- Helm 3+
- Git

## Setup Instructions

### 1. Start Minikube
```bash
minikube start
```

### 2. Enable Minikube Docker Environment
```bash
eval $(minikube docker-env)
```

### 3. Build Container Images
```bash
# Build frontend image
docker build -t todo-frontend:v1.0.0 ./frontend

# Build backend image
docker build -t todo-backend:v1.0.0 ./backend
```

### 4. Prepare Secrets
Create a values file with your secrets:
```bash
cat << EOF > my-values.yaml
secrets:
  jwtSecretKey: "your-base64-encoded-jwt-secret"
  databaseUrl: "your-base64-encoded-db-url"
  betterAuthSecret: "your-base64-encoded-auth-secret"
EOF
```

### 5. Install Helm Chart
```bash
helm install todo-app ./charts/todo-app -f my-values.yaml
```

### 6. Access the Application
```bash
# Get frontend service NodePort
kubectl get service frontend-service

# Access the application
minikube service frontend-service --url
```

## Verification
Check that all pods are running:
```bash
kubectl get pods
```

Check that services are accessible:
```bash
kubectl get services
```

## Troubleshooting
- If images don't load, ensure minikube docker-env is active during build
- If secrets are rejected, verify they are properly base64 encoded
- If services don't start, check resource limits and available cluster capacity

## Cleanup
```bash
helm uninstall todo-app
minikube stop
```