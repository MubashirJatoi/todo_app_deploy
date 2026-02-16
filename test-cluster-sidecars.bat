#!/bin/bash
# Script to test the Docker cluster with sidecar functionality

echo "Starting Docker cluster with sidecars..."
docker-compose up -d

echo "Waiting for services to start..."
sleep 30

echo "Checking running containers..."
docker-compose ps

echo "Testing backend service connectivity..."
curl -I http://localhost:8000/health 2>/dev/null || echo "Backend service not responding on :8000"

echo "Testing frontend service connectivity..."
curl -I http://localhost:3000 2>/dev/null || echo "Frontend service not responding on :3000"

echo "Testing Prometheus monitoring sidecar..."
curl -I http://localhost:9090 2>/dev/null || echo "Prometheus sidecar not responding on :9090"

echo "Testing Traefik dashboard..."
curl -I http://localhost:8080 2>/dev/null || echo "Traefik dashboard not responding on :8080"

echo "Checking logs for any errors..."
echo "=== Backend logs ==="
docker-compose logs backend | tail -10

echo "=== Frontend logs ==="
docker-compose logs frontend | tail -10

echo "=== Database logs ==="
docker-compose logs db | tail -10

echo "=== Sidecar logs ==="
docker-compose logs backend-logging-sidecar | tail -5
docker-compose logs backend-monitoring-sidecar | tail -5
docker-compose logs frontend-proxy-sidecar | tail -5
docker-compose logs db-backup-sidecar | tail -5

echo "Cluster test completed!"
echo "Services running:"
echo "- Backend API: http://localhost:8000"
echo "- Frontend: http://localhost:3000"
echo "- Prometheus (Monitoring): http://localhost:9090"
echo "- Traefik Dashboard: http://localhost:8080"
echo "- Proxy sidecar: http://localhost:8080"