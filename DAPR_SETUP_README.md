# Docker Compose with Dapr Sidecars

This setup implements the sidecar pattern using Dapr (Distributed Application Runtime) in a Docker Compose environment.

## Services Overview

- **Backend Service**: Main application backend with Dapr sidecar
- **Frontend Service**: Web interface with Dapr sidecar
- **Redis**: State store and pub/sub broker
- **Dapr Placement**: Dapr runtime component for actor placement
- **PostgreSQL**: Main database

## Architecture

In Docker Desktop, you'll see these services:

1. **Backend**: Shows as 2 linked containers (main + Dapr sidecar)
2. **Frontend**: Shows as 2 linked containers (main + Dapr sidecar)
3. **Redis**: Shows as 1 container
4. **Dapr Placement**: Shows as 1 container
5. **DB**: Shows as 1 container

## Running the Setup

### Prerequisites
- Docker Desktop with Docker Compose
- Dapr CLI (optional, for advanced operations)

### Starting Services

Windows Command Prompt:
```
start-dapr-services.bat
```

PowerShell:
```
.\start-dapr-services.ps1
```

Or manually:
```
docker-compose -f docker-compose-dapr.yml up -d
```

### Stopping Services

```
docker-compose -f docker-compose-dapr.yml down
```

## Accessing Services

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- Redis: localhost:6379
- PostgreSQL: localhost:5432

## Dapr Components

The setup includes:
- State management using Redis (statestore component)
- Pub/Sub messaging using Redis (pubsub component)

Both components are configured in the `dapr-components/` directory.

## Troubleshooting

If services don't start properly:
1. Check Docker Desktop is running
2. Verify all required files exist
3. Run `docker-compose -f docker-compose-dapr.yml logs` to see logs