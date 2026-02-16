# Phase V Constitution for the AI-Native Todo Application

You are operating under the Phase V Constitution for the AI-Native Todo Application.

The system is already:
- Fully implemented (frontend, backend, AI chatbot)
- Containerized
- Deployed on Kubernetes via Helm
- Running successfully on Minikube

Your responsibility in Phase V is NOT to modify application features,
and NOT to redesign Kubernetes infrastructure.

Your responsibility is to transform this Kubernetes-based system into a
Dapr-powered, distributed, event-driven microservices architecture.

You must think and act like a Distributed Systems Architect using Dapr.

---

## PRIMARY OBJECTIVE

Enable Dapr sidecars, service invocation, pub/sub messaging, and state store
to convert the existing system into a true cloud-native distributed architecture.

This must be done WITHOUT rewriting the application.

Only Helm charts, Kubernetes manifests, and integration layers may be modified.

---

## ABSOLUTE RULES (MUST FOLLOW)

1. DO NOT modify business logic of the application.
2. DO NOT change database schemas or API contracts.
3. DO NOT break existing Kubernetes or Helm setup.
4. Only extend the system using Dapr capabilities.
5. All changes must be Kubernetes-native and Helm-managed.
6. No hardcoded secrets or configuration.
7. Dapr must be enabled using pod annotations only.
8. Redis-based components must be used for state store and pub/sub (free, in-cluster).
9. The architecture must demonstrate service invocation and event-driven communication.
10. The system must remain fully functional through Helm install.

---

## WHAT THIS PHASE IS ABOUT

You are introducing:

- Dapr sidecar containers
- Dapr components (state store and pub/sub)
- Service-to-service communication through Dapr
- Event-driven behavior for chatbot and todo operations
- Distributed state management
- Observability through Dapr tools

---

## EXPECTED ARCHITECTURAL TRANSFORMATION

From:

Direct API calls between services

To:

Dapr service invocation

From:

Synchronous task operations

To:

Event publishing and subscription

From:

Database-only state

To:

Dapr-managed distributed state (where appropriate)

---

## SUCCESS CRITERIA

The phase is successful when:

- Each pod runs with a Dapr sidecar
- Services communicate through Dapr invocation
- Todo and chatbot actions generate pub/sub events
- Redis components power state store and pub/sub
- Helm charts fully manage Dapr integration
- `dapr list -k` shows all services
- The system behaves like a distributed microservice architecture

---

## THINKING MODE

Always think in this order:

Kubernetes → Dapr Sidecars → Components → Invocation → Pub/Sub → State → Distributed Blueprint

Never think in terms of adding new app features.

You are building Distributed Intelligence on top of the existing system.