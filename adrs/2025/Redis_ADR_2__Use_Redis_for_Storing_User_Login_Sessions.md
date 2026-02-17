ADR 2: Use Redis for Storing User Login Sessions 
Title: Store User Login Sessions in Redis 
Context:​
Our system requires user logins, and we need to store user sessions without relying on a single 
server’s memory (stateless approach). 
Decision:​
We decided to use Redis to store user sessions using a session token or JWT as the key. 
Rationale: 
●​ Redis is fast and supports distributed session storage. 
●​ It allows setting an expiration time for sessions. 
●​ It is easier to scale out compared to storing sessions in server memory. 
Consequences: 
●​ Pros: Supports load balancing and reduces the burden on application servers. 
●​ Cons: If Redis goes down, users may need to log in again. 
Sample Code:
