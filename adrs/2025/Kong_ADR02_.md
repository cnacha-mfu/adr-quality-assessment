ADR 002: Implement Authentication with Kong JWT Plugin 
Title  
Using Kong JWT Plugin for API Authentication  
Context  
In our system, we require secure authentication and authorization mechanisms for API access. 
Traditional session-based authentication is inefficient for microservices and stateless API 
architectures.  
To ensure scalability and security, we need a token-based authentication system. 
Using Kong’s JWT Plugin, we can:  
Secure API endpoints without modifying backend services  
Validate JWT tokens at the gateway level  
Reduce the need for database lookups for authentication  
Decision  
We have decided to implement Kong JWT Plugin as our authentication mechanism. Key 
reasons include:  
● Decoupled Authentication: API services do not need to handle token validation. ● 
Improved Performance: Kong validates tokens without querying a database. ● 
Compatibility: Supports OAuth2 Providers, allowing easy integration with third-party 
authentication systems.  
● Security: Reduces risks associated with session hijacking and replay attacks. 
Consequences  
● Positive Outcomes:  
○ Secure & Scalable Authentication  
○ Reduced Backend Load 
○ Simplified Token Management  
● Potential Drawbacks:  
○ Token Expiration – Requires users to refresh tokens periodically.  

○ Initial Setup Complexity – Requires defining Consumers and JWT Credentials in 
Kong.  
Sample Implementation  
● Enable JWT Plugin for an API Service  
curl -i -X POST http://localhost:8001/services/my-service/plugins \  
--data "name=jwt"  
● Create a Consumer (API Client)  
curl -i -X POST http://localhost:8001/consumers/ \  
--data "username=demo-user"  
● Generate JWT Credentials for the Consumer  
curl -i -X POST http://localhost:8001/consumers/demo-user/jwt  
● Retrieve and Use the JWT Token  
curl -i -X GET http://localhost:8000/api/v1 \  
-H "Authorization: Bearer <your-jwt-token>"
