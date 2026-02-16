#!/bin/bash
# Script to run the Docker Compose setup with Dapr sidecars

echo "Starting Docker Compose with Dapr sidecars..."
echo "This will create:"
echo "  - backend service + Dapr sidecar (shown as 2 containers linked)"
echo "  - frontend service + Dapr sidecar (shown as 2 containers linked)" 
echo "  - redis service (shown as 1 container)"
echo "  - dapr-placement service (shown as 1 container)"
echo "  - db service (shown as 1 container)"

# Start the services
docker-compose -f docker-compose-dapr.yml up -d

echo "Waiting for services to start..."
sleep 30

echo "Checking running containers..."
docker-compose -f docker-compose-dapr.yml ps

echo ""
echo "Services should now be running:"
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:3000" 
echo "  - Redis: localhost:6379"
echo "  - PostgreSQL: localhost:5432"

echo ""
echo "To view logs:"
echo "  - Backend: docker-compose -f docker-compose-dapr.yml logs backend"
echo "  - Frontend: docker-compose -f docker-compose-dapr.yml logs frontend"
echo "  - Redis: docker-compose -f docker-compose-dapr.yml logs redis"

echo ""
echo "To stop the services:"
echo "  docker-compose -f docker-compose-dapr.yml down"