# Dapr Component Pub/Sub Skill

## Purpose
Define and create Dapr pub/sub component YAML manifests for event-driven messaging.

## What it does
- Creates pub/sub component YAML files (Redis Streams, Kafka, RabbitMQ)
- Configures message broker connection strings and authentication
- Sets up consumer groups and delivery guarantees
- Defines topics, subscriptions, and message routing
- Configures dead letter queues and retry policies

## What it does NOT do
- Implement event publishers or subscribers in application code
- Install or manage message broker infrastructure
- Define event schemas or business logic

## Usage
Use this skill when you need to:
- Create a new pub/sub component for event-driven architecture
- Configure message broker connections and credentials
- Set up pub/sub scopes for different microservices
- Configure retry and dead letter queue policies

## Example
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: default
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis-master:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis-secret
      key: password
  - name: consumerID
    value: "backend-consumer"
  - name: redeliverInterval
    value: "30s"
  scopes:
  - backend-app
  - chatbot-app
```
