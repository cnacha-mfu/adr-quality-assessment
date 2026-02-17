ADR 1: Use Redis for Caching 
Title: Implement Caching with Redis 
Context:​
Our system frequently reads data from the database, and some of this data is relatively static 
(e.g., constants or frequently reused data). Accessing the database directly each time slows 
down the system and places a high load on the database. 
Decision:​
We decided to use Redis as a caching layer to store frequently accessed data, thereby 
reducing direct database access. 
Rationale: 
●​ Redis operates in-memory, allowing for very fast data retrieval. 
●​ It supports setting expiration times (TTL) for cached data. 
●​ It scales well to handle high traffic. 
Consequences: 
●​ Pros: Reduces database read load and improves system performance. 
●​ Cons: Requires a proper cache invalidation strategy to avoid serving stale data. 
Sample Code:
