# PowerShell script to test the Docker cluster with sidecar functionality

Write-Host "Starting Docker cluster with sidecars..." -ForegroundColor Green
docker-compose up -d

Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "Checking running containers..." -ForegroundColor Green
docker-compose ps

Write-Host "Testing backend service connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Head -TimeoutSec 10
    Write-Host "Backend service is responding" -ForegroundColor Green
} catch {
    Write-Host "Backend service not responding on :8000" -ForegroundColor Red
}

Write-Host "Testing frontend service connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method Head -TimeoutSec 10
    Write-Host "Frontend service is responding" -ForegroundColor Green
} catch {
    Write-Host "Frontend service not responding on :3000" -ForegroundColor Red
}

Write-Host "Testing Prometheus monitoring sidecar..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090" -Method Head -TimeoutSec 10
    Write-Host "Prometheus sidecar is responding" -ForegroundColor Green
} catch {
    Write-Host "Prometheus sidecar not responding on :9090" -ForegroundColor Red
}

Write-Host "Testing Traefik dashboard..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -Method Head -TimeoutSec 10
    Write-Host "Traefik dashboard is responding" -ForegroundColor Green
} catch {
    Write-Host "Traefik dashboard not responding on :8080" -ForegroundColor Red
}

Write-Host "`nChecking logs for any errors..." -ForegroundColor Green
Write-Host "=== Backend logs ===" -ForegroundColor Cyan
docker-compose logs backend | Select-Object -Last 10

Write-Host "`n=== Frontend logs ===" -ForegroundColor Cyan
docker-compose logs frontend | Select-Object -Last 10

Write-Host "`n=== Database logs ===" -ForegroundColor Cyan
docker-compose logs db | Select-Object -Last 10

Write-Host "`n=== Sidecar logs ===" -ForegroundColor Cyan
docker-compose logs backend-logging-sidecar | Select-Object -Last 5
docker-compose logs backend-monitoring-sidecar | Select-Object -Last 5
docker-compose logs frontend-proxy-sidecar | Select-Object -Last 5
docker-compose logs db-backup-sidecar | Select-Object -Last 5

Write-Host "`nCluster test completed!" -ForegroundColor Green
Write-Host "Services running:" -ForegroundColor White
Write-Host "- Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "- Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "- Prometheus (Monitoring): http://localhost:9090" -ForegroundColor White
Write-Host "- Traefik Dashboard: http://localhost:8080" -ForegroundColor White
Write-Host "- Proxy sidecar: http://localhost:8080" -ForegroundColor White