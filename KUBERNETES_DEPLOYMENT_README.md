# Todo App Kubernetes Deployment

This project contains a full-stack todo application with Next.js frontend and FastAPI backend, designed for deployment to Kubernetes using Helm charts.

## Deployment Instructions

### Prerequisites
1. Docker Desktop running
2. Minikube installed
3. Helm installed
4. At least 4GB free disk space on D: drive (due to C: drive space constraints)

### Deployment Steps

1. **Ensure Docker Desktop is running** on your system.

2. **Run the deployment script**:
   ```cmd
   deploy-to-minikube.bat
   ```

   This script will:
   - Create Minikube configuration on the D: drive
   - Start a Minikube cluster with Docker driver
   - Deploy the application using Helm
   - Show the deployment status

3. **Access the application**:
   After successful deployment, use the following command to access the frontend:
   ```cmd
   minikube service frontend-svc -n todo-app --profile=tododeploy
   ```

### Alternative Manual Steps

If the script doesn't work, follow these manual steps:

1. Set up Minikube on D: drive:
   ```cmd
   mkdir D:\minikube-data
   set MINIKUBE_HOME=D:\minikube-data
   minikube start --profile=tododeploy --driver=docker --memory=2048mb --cpus=2 --disk-size=4g
   ```

2. Configure Docker for Minikube:
   ```cmd
   FOR /f "tokens=*" %i IN ('minikube docker-env --profile=tododeploy') DO %i
   ```

3. Deploy with Helm:
   ```cmd
   helm install todo-app ./charts/todo-app/ -f minikube-values.yaml --create-namespace --namespace todo-app
   ```

### Architecture
- Frontend: Next.js application (Node.js)
- Backend: FastAPI application (Python)
- Database: PostgreSQL
- Containerized with Docker
- Orchestrated with Kubernetes
- Deployed using Helm charts

### Configuration
The deployment uses `minikube-values.yaml` which is optimized for resource-constrained environments with:
- Reduced memory and CPU requests
- Local image pulling strategy
- NodePort service type for easy access