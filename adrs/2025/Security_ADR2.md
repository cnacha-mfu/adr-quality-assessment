ADR2: Implementing JWT with Refresh Tokens for 
Session Management 
Title:Implementing JWT with Refresh Tokens for Session Management  
Context 
JWTs have a fixed expiration time, and once expired, users need to log in again. This creates a 
poor user experience for long sessions. To solve this, refresh tokens allow issuing new access 
tokens without requiring users to re-authenticate. 
Decision 
●​ Implement refresh tokens along with JWT-based authentication. 
●​ Store refresh tokens securely in an HTTP-only cookie. 
●​ Refresh tokens will have a longer expiration time than access tokens. 
●​ Implement token rotation to prevent reuse of old refresh tokens. 
Rationale 
●​ Improves user experience by allowing seamless re-authentication without requiring 
login. 
●​ Enhances security by using token rotation to mitigate token theft risks. 
●​ Access tokens remain short-lived, reducing the impact of token leaks. 
Consequences 
Pros: 
●​ Improves session management and user experience. 
●​ Short-lived access tokens reduce security risks. 
●​ Refresh token rotation prevents misuse of stolen tokens. 
Cons: 
●​ Requires additional storage for refresh tokens (e.g., secure database storage). 
●​ If not managed properly, refresh token leaks can lead to prolonged unauthorized 
access. 
●​ Extra API calls for token refresh add minor overhead. 
Sample Code 
Generating Access and Refresh Tokens 

 
const accessToken = jwt.sign({ userId: 123 }, privateKey, { algorithm: 'RS256', expiresIn: '15m' 
}); 
const refreshToken = jwt.sign({ userId: 123 }, privateKey, { algorithm: 'RS256', expiresIn: '7d' }); 
console.log({ accessToken, refreshToken }); 
 
Refreshing Tokens 
 
const newAccessToken = jwt.sign({ userId: decoded.userId }, privateKey, { algorithm: 'RS256', 
expiresIn: '15m' }); 
console.log(newAccessToken);
