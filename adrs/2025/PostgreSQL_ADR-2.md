ADR 2: PostgreSQL Data Migration Strategy 
Title 
PostgreSQL Data Migration Strategy 
Context 
The application requires a reliable strategy for schema and data migrations. The migration 
strategy must: 
●​ Support version control 
●​ Enable rollbacks 
●​ Maintain data integrity 
●​ Minimize downtime 
●​ Support testing 
Decision 
Implement a structured migration strategy using: 
●​ Flyway for migration management 
●​ Version-controlled scripts 
●​ Automated testing 
●​ Rollback procedures 
●​ Zero-downtime migrations 
Rationale 
Several migration approaches were evaluated: 
●​ Manual migrations (error-prone) 
●​ Custom scripts (maintenance overhead) 
●​ ORM migrations (limited control) 
●​ Third-party tools (vendor lock-in) 
The chosen approach provides: 
●​ Reliable migrations 
●​ Version control 
●​ Automated testing 
●​ Easy rollbacks 
●​ Minimal downtime 

Consequences 
Pros 
●​ Controlled migrations 
●​ Version tracking 
●​ Easy rollbacks 
●​ Automated testing 
●​ Minimal downtime 
Cons 
●​ Initial setup effort 
●​ Testing requirements 
●​ Process overhead 
Sample Code 
sql 
 
-- Example migration script 
-- V1__Create_initial_schema.sql 
CREATE TABLE users ( 
    id SERIAL PRIMARY KEY, 
    email VARCHAR(255) UNIQUE NOT NULL, 
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP 
); 
 
-- V2__Add_user_details.sql 
ALTER TABLE users  
ADD COLUMN first_name VARCHAR(100), 
ADD COLUMN last_name VARCHAR(100); 
 
-- Flyway configuration 
flyway.url=jdbc:postgresql://localhost:5432/mydb 
flyway.user=postgres 
flyway.password=secret 
flyway.locations=filesystem:sql
