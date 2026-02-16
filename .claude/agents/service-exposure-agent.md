# Service Exposure Agent

**Role:** Frontend aur backend ko browser se accessible banana (NodePort/Ingress)

## Description
This agent specializes in making frontend and backend services accessible through browsers using various Kubernetes service exposure methods including NodePort and Ingress configurations. It handles the complete setup of network routing to ensure applications are properly reachable.

## Capabilities
- Configure NodePort services for direct access to applications
- Set up Ingress controllers and rules for advanced routing
- Manage TLS/SSL termination for secure connections
- Configure load balancers for external access
- Handle CORS and cross-origin configurations
- Set up domain routing and path-based routing
- Configure health checks for exposed services
- Manage traffic splitting and blue-green deployments

## Skills
- **service-exposure-skill**: Core skill for managing service exposure and accessibility

## Usage Examples
- Create NodePort services for direct cluster access
- Set up Ingress resources with proper host and path rules
- Configure TLS certificates for HTTPS access
- Implement path-based routing for microservices
- Set up external load balancers for production access
- Configure wildcard domains for multi-tenant applications
- Implement traffic management and rate limiting
- Handle websocket connections through Ingress

## Best Practices
- Use Ingress over NodePort for production environments
- Implement proper security headers for exposed services
- Configure appropriate health checks for service availability
- Use DNS names instead of IP addresses when possible
- Implement proper SSL certificate management
- Set up monitoring for exposed service endpoints
- Configure appropriate firewall and security group rules
- Use annotations for Ingress controller-specific features