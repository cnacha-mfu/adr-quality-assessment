Docker Containerization 
Decision Record 2: Using Docker for Dependency 
Management 
 Context 
Our development team uses different operating systems, leading to dependency conflicts 
when setting up the project. Some machines have different Java versions or SQL Server 
drivers, causing inconsistencies. 
 Decision 
We will containerize the Spring Boot backend and SQL Server database using Docker. This 
ensures that every developer works in the same environment without needing manual setup. 
 Rationale 
●​ Eliminates dependency issues by using a single, standardized Docker image. 
●​ Allows quick onboarding for new developers. 
●​ Works seamlessly in development, testing, and production. 
 Consequences 
 Pros: 
●​ Ensures the app runs the same everywhere. 
●​ Simplifies setup—just run docker-compose up. 
●​ Avoids version conflicts. 
 Cons: 
●​ Larger image sizes (especially for SQL Server). 
●​ Learning curve for developers new to Docker. 
 
 
 
 

 Sample Code 
Dockerfile for Spring Boot Backend: 
 
FROM openjdk:21-jdk-slim 
WORKDIR /app 
COPY target/ambulance-app.jar app.jar 
EXPOSE 8080 
CMD ["java", "-jar", "app.jar"] 
 
 
Docker Compose for Backend + Database: 
version: '3.8' 
services: 
  backend: 
    build: . 
    ports: 
      - "8080:8080" 
    depends_on: 
      - database 
 
  database: 
    image: mcr.microsoft.com/mssql/server:latest 
    environment: 
      SA_PASSWORD: "YourStrong!Passw0rd" 
      ACCEPT_EULA: "Y" 
    ports: 
      - "1433:1433"
