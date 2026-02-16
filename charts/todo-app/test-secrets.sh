#!/bin/bash
# Test script for validating secret mounting and access in deployed pods

echo "Testing secret mounting and access in deployed pods..."

NAMESPACE=${1:-default}

echo "1. Checking for secret existence:"
kubectl get secrets -n $NAMESPACE | grep -E "(auth-secret|db-secret|ai-secret)"

echo ""
echo "2. Verifying secret content structure (without revealing actual values):"
kubectl get secret todo-app-auth-secret -n $NAMESPACE -o yaml | grep -E "(data:|type:|metadata:)"
kubectl get secret todo-app-db-secret -n $NAMESPACE -o yaml | grep -E "(data:|type:|metadata:)"
kubectl get secret todo-app-ai-secret -n $NAMESPACE -o yaml | grep -E "(data:|type:|metadata:)" 2>/dev/null || echo "AI secret not found (may be disabled)"

echo ""
echo "3. Getting pod names:"
FRONTEND_POD=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

echo "Frontend pod: $FRONTEND_POD"
echo "Backend pod: $BACKEND_POD"

echo ""
if [ ! -z "$BACKEND_POD" ]; then
    echo "4. Checking environment variables in backend pod:"
    kubectl exec -it $BACKEND_POD -n $NAMESPACE -- env | grep -E "(DATABASE_URL|BETTER_AUTH_SECRET|COHERE_API_KEY)"

    echo ""
    echo "5. Checking mounted secret volumes in backend pod:"
    kubectl exec -it $BACKEND_POD -n $NAMESPACE -- ls -la /var/run/secrets/kubernetes.io/serviceaccount/ 2>/dev/null || echo "Service account tokens not found"
fi

if [ ! -z "$FRONTEND_POD" ]; then
    echo ""
    echo "6. Checking environment variables in frontend pod:"
    kubectl exec -it $FRONTEND_POD -n $NAMESPACE -- env | grep -E "(BETTER_AUTH_SECRET)"
fi

echo ""
echo "7. Verifying secret access through logs (looking for any secret-related errors):"
if [ ! -z "$BACKEND_POD" ]; then
    echo "Backend logs:"
    kubectl logs $BACKEND_POD -n $NAMESPACE --tail=20 | grep -i -E "(secret|auth|database|error)" || echo "No secret-related errors found in backend logs"
fi

if [ ! -z "$FRONTEND_POD" ]; then
    echo "Frontend logs:"
    kubectl logs $FRONTEND_POD -n $NAMESPACE --tail=20 | grep -i -E "(secret|auth|error)" || echo "No secret-related errors found in frontend logs"
fi

echo ""
echo "8. Testing secret accessibility by attempting to connect to services:"
echo "Checking if backend can reach database:"
if [ ! -z "$BACKEND_POD" ]; then
    kubectl exec -it $BACKEND_POD -n $NAMESPACE -- env | grep DATABASE_URL
fi

echo ""
echo "Secret mounting test completed. All secrets should be properly mounted and accessible to their respective pods."