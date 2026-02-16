#!/bin/bash
# Script to set up Minikube on D: drive and deploy the todo app

# Create directory on D: drive for Minikube
mkdir -p /d/minikube-data

# Set the MINIKUBE_HOME environment variable
export MINIKUBE_HOME=/d/minikube-data

# Start Minikube with minimal resources
minikube start --profile=tododeploy --driver=docker --memory=2048mb --cpus=2 --disk-size=4g --kubernetes-version=v1.28.3

# Verify Minikube is running
minikube status --profile=tododeploy

# Load the Docker images into Minikube's container registry
eval $(minikube docker-env --profile=tododeploy)
docker images
docker tag todo-backend:latest todo-backend:latest
docker tag todo-frontend:latest todo-frontend:latest

# Deploy the application using Helm
helm install todo-app ./charts/todo-app/ -f minikube-values.yaml --create-namespace --namespace todo-app