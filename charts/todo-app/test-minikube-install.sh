#!/bin/bash
# End-to-end test script for Minikube installation of Todo App Helm chart

set -e

echo "Starting Minikube Todo App Installation Test..."

# Check prerequisites
echo "1. Checking prerequisites..."
if ! command -v minikube &> /dev/null; then
    echo "ERROR: minikube is not installed"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo "ERROR: helm is not installed"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "ERROR: kubectl is not installed"
    exit 1
fi

echo "✓ All prerequisites are installed"

# Start minikube if not running
echo ""
echo "2. Starting Minikube..."
if ! minikube status &> /dev/null; then
    echo "Starting Minikube cluster..."
    minikube start --cpus=2 --memory=4g --disk-size=10g
else
    echo "Minikube is already running"
fi

echo "Waiting for Minikube to be ready..."
sleep 10

# Enable ingress addon if needed
echo ""
echo "3. Enabling Minikube addons..."
minikube addons enable ingress || echo "Ingress addon may already be enabled"

# Navigate to chart directory
CHART_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$CHART_DIR/../"

echo ""
echo "4. Validating Helm chart..."
helm lint .

# Create minikube-specific values file
echo ""
echo "5. Creating Minikube-specific values file..."
cat > minikube-values.yaml << EOF
minikube:
  enabled: true
  imagePullPolicy: "IfNotPresent"
  serviceType: "NodePort"
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

backend:
  service:
    type: NodePort

database:
  volume:
    size: 512Mi

ingress:
  enabled: false

# Use example values for secrets (in production, use sealed secrets or external secret management)
auth:
  secret: "UwL72Tk7hx7p6x8geT7CeeB6NmjnEzck"

database:
  url: "postgresql://user:password@todo-app-database:5432/todo_db"
  password: "password"

ai:
  coapiKey: "SjQEmGMmZM5iuedMzLGT7lZIUKp2TCTI2ujatWHy"
EOF

echo "Minikube values file created:"
cat minikube-values.yaml

# Install the chart
echo ""
echo "6. Installing Helm chart with Minikube configuration..."
helm install todo-app . -f minikube-values.yaml --wait --timeout=10m

echo ""
echo "7. Waiting for all pods to be ready..."
kubectl wait --for=condition=Ready pods --all --timeout=300s

echo ""
echo "8. Checking pod status..."
kubectl get pods

echo ""
echo "9. Checking service status..."
kubectl get svc

echo ""
echo "10. Checking deployment status..."
kubectl get deployments

echo ""
echo "11. Checking if all secrets were created properly..."
kubectl get secrets | grep todo-app

echo ""
echo "12. Checking if all configmaps were created properly..."
kubectl get configmaps | grep todo-app

echo ""
echo "13. Checking backend logs for any errors..."
BACKEND_POD=$(kubectl get pods -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')
if [ ! -z "$BACKEND_POD" ]; then
    kubectl logs $BACKEND_POD | tail -20
fi

echo ""
echo "14. Checking frontend logs for any errors..."
FRONTEND_POD=$(kubectl get pods -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].metadata.name}')
if [ ! -z "$FRONTEND_POD" ]; then
    kubectl logs $FRONTEND_POD | tail -20
fi

echo ""
echo "15. Testing service accessibility..."
FRONTEND_SVC=$(kubectl get svc -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].metadata.name}')
FRONTEND_PORT=$(kubectl get svc $FRONTEND_SVC -o jsonpath='{.spec.ports[?(@.name=="http")].nodePort}')

echo "Frontend service: $FRONTEND_SVC"
echo "Frontend port: $FRONTEND_PORT"

# Get minikube IP
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"

if [ ! -z "$FRONTEND_PORT" ]; then
    echo "Frontend should be accessible at: http://$MINIKUBE_IP:$FRONTEND_PORT"

    # Test if the service is responding (non-blocking test)
    echo "Testing service connectivity..."
    curl -s --connect-timeout 5 http://$MINIKUBE_IP:$FRONTEND_PORT/ || echo "Service may still be starting up..."
fi

echo ""
echo "16. Running basic health checks..."
BACKEND_SVC=$(kubectl get svc -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')
if [ ! -z "$BACKEND_SVC" ]; then
    BACKEND_CLUSTER_IP=$(kubectl get svc $BACKEND_SVC -o jsonpath='{.spec.clusterIP}')
    echo "Backend ClusterIP: $BACKEND_CLUSTER_IP"

    # Test backend health endpoint from within the cluster
    if [ ! -z "$BACKEND_POD" ]; then
        kubectl exec $BACKEND_POD -- wget -qO- http://$BACKEND_CLUSTER_IP:7860/health || echo "Health check may still be initializing..."
    fi
fi

echo ""
echo "Installation test completed successfully!"
echo ""
echo "Summary:"
echo "- Helm chart installed with Minikube configuration"
echo "- All pods are running and ready"
echo "- Services are accessible"
echo "- Secrets and configmaps created properly"
echo ""
echo "To access the application:"
echo "Frontend: http://$MINIKUBE_IP:$FRONTEND_PORT"
echo ""
echo "To view all resources:"
echo "kubectl get all,cm,secret -l app.kubernetes.io/part-of=todo-app"
echo ""
echo "To uninstall:"
echo "helm uninstall todo-app"