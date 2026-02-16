# PowerShell script to run the Docker Compose setup with Dapr sidecars

Write-Host "Starting Docker Compose with Dapr sidecars..." -ForegroundColor Green
Write-Host "This will create:" -ForegroundColor Yellow
Write-Host "  - backend service + Dapr sidecar (shown as 2 containers linked)" -ForegroundColor Yellow
Write-Host "  - frontend service + Dapr sidecar (shown as 2 containers linked)" -ForegroundColor Yellow
Write-Host "  - redis service (shown as 1 container)" -ForegroundColor Yellow
Write-Host "  - dapr-placement service (shown as 1 container)" -ForegroundColor Yellow
Write-Host "  - db service (shown as 1 container)" -ForegroundColor Yellow

# Start the services
Write-Host "`nStarting services..." -ForegroundColor Green
docker-compose -f docker-compose-dapr.yml up -d

Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "Checking running containers..." -ForegroundColor Green
docker-compose -f docker-compose-dapr.yml ps

Write-Host "" 
Write-Host "Services should now be running:" -ForegroundColor Green
Write-Host "  - Backend: http://localhost:8000" -ForegroundColor White
Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  - Redis: localhost:6379" -ForegroundColor White
Write-Host "  - PostgreSQL: localhost:5432" -ForegroundColor White

Write-Host ""
Write-Host "To view logs:" -ForegroundColor Green
Write-Host "  - Backend: docker-compose -f docker-compose-dapr.yml logs backend" -ForegroundColor White
Write-Host "  - Frontend: docker-compose -f docker-compose-dapr.yml logs frontend" -ForegroundColor White
Write-Host "  - Redis: docker-compose -f docker-compose-dapr.yml logs redis" -ForegroundColor White

Write-Host ""
Write-Host "To stop the services:" -ForegroundColor Green
Write-Host "  docker-compose -f docker-compose-dapr.yml down" -ForegroundColor White