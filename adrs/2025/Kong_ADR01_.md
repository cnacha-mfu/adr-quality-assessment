Architecture Decision Record (ADR): API Gateway with 
Kong 
ADR 001 : Use Kong as API Gateway  
Title 
Using Kong as an API Gateway for centralized API management 
Context 
As our system grows, managing APIs efficiently becomes a challenge. We need a centralized 
API Gateway to handle: 
​
•​
Authentication & Authorization (OAuth2, JWT, API Keys) 
​
•​
Rate Limiting & Load Balancing 
​
•​
Logging & Monitoring 
​
•​
Request Routing & API Versioning 
Kong is a popular API Gateway that provides these features along with extensibility through 
plugins. 
Additionally, offloading authentication to Kong using its JWT Plugin helps reduce backend 
workload and enhances security. 
Decision 
We have decided to implement Kong API Gateway for managing our APIs. The key reasons for 
this decision include: 
●​ Scalability: Built on NGINX, Kong is optimized for high-performance API traffic. 
●​ Plugin System: Supports a wide range of authentication, logging, and transformation 
plugins. 
●​ Performance: Low-latency request processing. 
●​ Flexible Deployment: Available in Open-Source & Enterprise Editions, supporting 
Kubernetes, Docker, and traditional servers. 
●​ Security: Supports OAuth2, JWT, API Keys, and other authentication mechanisms. 

For authentication, we will utilize Kong’s JWT Plugin, allowing clients to authenticate API 
requests using JWT tokens instead of session-based authentication.o 
Consequences 
●​ Positive Outcomes: 
○​ Centralized API management 
○​ Improved security and observability 
○​ Simplified API versioning and maintenance 
○​ Reduced Backend Load 
●​ Potential Drawbacks: 
○​ Learning curve for configuring and managing Kong 
○​ Additional infrastructure costs for deployment and maintenance 
Sample Code 
●​ Adding a New API Service in Kong 
curl -i -X POST http://localhost:8001/services/ \ 
  --data "name=my-service" \ 
  --data "url=http://backend-service:8080" 
●​ Adding a Route for the API Service 
curl -i -X POST http://localhost:8001/services/my-service/routes \ 
  --data "paths[]=/api/v1" 
●​ Enabling JWT Authentication 
curl -i -X POST http://localhost:8001/services/my-service/plugins \ 
  --data "name=jwt" 
●​ a Consumer for API Access 
curl -i -X POST http://localhost:8001/consumers/ \ 
  --data "username=demo-user" 
●​ Generating JWT Credentials for the Consumer 
curl -i -X POST http://localhost:8001/consumers/demo-user/jwt 

●​ Making an Authenticated API Request Using JWT 
curl -i -X GET http://localhost:8000/api/v1 \ 
  -H "Authorization: Bearer <your-jwt-token>"
