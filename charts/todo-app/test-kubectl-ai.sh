#!/bin/bash
# Test script for kubectl-ai inspection of deployed resources

echo "Testing kubectl-ai inspection of deployed resources..."

echo "1. Listing all resources with AI-related labels:"
kubectl get all,cm,secret,pvc -l ai/managed=true --all-namespaces

echo ""
echo "2. Inspecting frontend deployment with AI annotations:"
kubectl describe deployment todo-app-frontend -n default | grep -A 20 -B 5 "ai/"

echo ""
echo "3. Inspecting backend deployment with AI annotations:"
kubectl describe deployment todo-app-backend -n default | grep -A 20 -B 5 "ai/"

echo ""
echo "4. Checking all resources with discoverable label:"
kubectl get all,cm,secret,pvc -l ai/discoverable=true --all-namespaces

echo ""
echo "5. Inspecting resource health status:"
kubectl get pods,services,deployments,hpa -o wide

echo ""
echo "6. Checking metrics endpoints availability:"
kubectl get svc -l service-type=metrics

echo ""
echo "7. Verifying AI-related annotations across all resources:"
kubectl get all,cm,secret,pvc -o json | jq '.items[] | select(.metadata.annotations | has("ai/managed")) | {kind: .kind, name: .metadata.name, namespace: .metadata.namespace, annotations: .metadata.annotations}'

echo ""
echo "Test completed. All resources should show proper AI annotations and be discoverable by kagent tools."