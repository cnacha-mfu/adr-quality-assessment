Docker Containerization 
 
Decision Record 1: Using Microservices for an 
Ambulance Web App 
 Context 
Our ambulance web application is currently monolithic, making it difficult to scale or update 
specific features independently. As the system grows, maintaining and debugging the code 
becomes more complex. 
 Decision 
 We will refactor the app into microservices, separating key functionalities such as: 
●​ Emergency Service  – Handles emergency case creation. 
●​ User Service  – Manages authentication and user roles. 
●​ Location Service  – Manages real-time ambulance tracking. 
 Each service will run in a Docker container and communicate via REST APIs. 
 Rationale 
●​ Enables independent scaling (e.g., scaling Emergency Service separately). 
●​ Allows teams to work on different services without conflicts. 
●​ Easier maintenance and faster deployment cycles. 
 Consequences 
  Pros: 
●​ Better scalability and flexibility. 
●​ Services can be deployed independently. 
●​ Reduced risk of breaking the entire system with changes. 
  Cons: 
●​ More complex deployment (requires managing multiple services). 
●​ Increased inter-service communication overhead. 
 

Sample Code 
version: '3.8' 
services: 
  emergency-service: 
    image: ambulance-emergency:latest 
    ports: 
      - "5001:5001" 
 
  user-service: 
    image: ambulance-user:latest 
    ports: 
      - "5002:5002" 
 
  location-service: 
    image: ambulance-location:latest 
    ports: 
      - "5003:5003"
