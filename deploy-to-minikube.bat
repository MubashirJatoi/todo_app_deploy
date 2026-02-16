@echo off
REM Batch script to deploy Todo app to Minikube
REM Run this script after ensuring Docker Desktop is running

echo Creating directory on D: drive for Minikube...
if not exist "D:\minikube-data" mkdir "D:\minikube-data"

echo Setting MINIKUBE_HOME environment variable...
set MINIKUBE_HOME=D:\minikube-data

echo Starting Minikube with Docker driver...
minikube start --profile=tododeploy --driver=docker --memory=2048mb --cpus=2 --disk-size=4g

if %ERRORLEVEL% NEQ 0 (
    echo Failed to start Minikube. Please ensure Docker Desktop is running.
    pause
    exit /b %ERRORLEVEL%
)

echo Minikube started successfully. Setting Docker environment...
for /f "tokens=*" %%i in ('minikube docker-env --profile=tododeploy') do %%i

echo Verifying Docker images...
docker images | findstr todo

echo Deploying application using Helm...
helm install todo-app ./charts/todo-app/ -f minikube-values.yaml --create-namespace --namespace todo-app

echo Checking deployment status...
kubectl get pods -n todo-app
kubectl get svc -n todo-app

echo.
echo Deployment completed! Access the application using:
echo minikube service frontend-svc -n todo-app --profile=tododeploy
echo.
pause