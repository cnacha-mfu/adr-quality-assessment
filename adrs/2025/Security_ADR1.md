ADR 1: Implementing JWT for Secure API Authentication 
 
Title:Implementing JWT for Secure API Authentication 
Context 
Modern applications require a secure and scalable authentication mechanism that allows 
stateless authorization across distributed systems. Traditional session-based authentication 
requires storing session data on the server, which introduces scalability challenges. JWT (JSON 
Web Tokens) provides a stateless mechanism where authentication information is encoded into 
a compact token, reducing the need for server-side session storage. 
Decision 
●​ Use JWT (JSON Web Tokens) as the primary authentication mechanism for API 
security. 
●​ Implement RS256 (asymmetric encryption) instead of HS256 (symmetric encryption) 
for token signing. 
●​ Include user roles and permissions inside JWT claims for access control. 
●​ Store JWTs in HTTP-only cookies to protect against XSS attacks. 
●​ Implement token expiration and refresh tokens to manage session validity. 
Rationale 
●​ JWTs are stateless, allowing authentication to scale across multiple services without 
storing session data on the server. 
●​ RS256 asymmetric signing ensures that tokens can be verified without exposing the 
private key. 
●​ Claims-based authentication allows embedding user data for fine-grained access 
control. 
●​ Using HTTP-only cookies prevents tokens from being accessed by client-side scripts, 
reducing security risks. 
Consequences 
Pros: 
●​ Stateless authentication improves scalability and performance. 
●​ JWTs work across different platforms and services. 
●​ Built-in expiration mechanisms reduce the risk of token misuse. 
●​ Improved security with asymmetric encryption (RS256). 
Cons: 

●​ Larger token size compared to session IDs due to payload encoding. 
●​ Token revocation is difficult, requiring strategies like short expiration or blocklists. 
●​ Sensitive data inside JWT claims must be minimized to avoid information leaks. 
Sample Code 
Generating JWT with RS256 (Node.js Example) 
 
const jwt = require('jsonwebtoken'); 
const fs = require('fs'); 
 
const privateKey = fs.readFileSync('private.pem'); 
const token = jwt.sign({ userId: 123, role: 'admin' }, privateKey, { algorithm: 'RS256', expiresIn: 
'1h' }); 
console.log(token); 
 
 
Verifying JWT with RS256 
 
const publicKey = fs.readFileSync('public.pem'); 
const decoded = jwt.verify(token, publicKey, { algorithms: ['RS256'] }); 
console.log(decoded);
