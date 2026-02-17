ADR 1: Selecting PostgreSQL as Primary Database 
System 
Title 
Selecting PostgreSQL as Primary Database System 
Context 
The application requires a robust, scalable, and feature-rich database system that can handle 
complex queries, maintain data integrity, and support modern application development patterns. 
The database system needs to support: 
●​ Complex data types and relationships 
●​ High concurrent user access 
●​ Advanced querying capabilities 
●​ Data integrity and ACID compliance 
●​ Extensibility and custom functions 
●​ Geographic data storage and queries 
●​ Full-text search capabilities 
Decision 
PostgreSQL will be implemented as the primary database system due to its robust feature set, 
reliability, and extensive community support. The decision includes using PostgreSQL 15 or 
later versions to leverage the latest performance improvements and features. 
Rationale 
Several database systems were evaluated before selecting PostgreSQL: 
●​ MySQL offers good performance but lacks some advanced features 
●​ Oracle Database provides enterprise features but has high licensing costs 
●​ MongoDB offers flexibility but sacrifices ACID compliance 
●​ Microsoft SQL Server requires Windows expertise and has licensing costs 
PostgreSQL was selected because it: 
●​ Is open-source with no licensing costs 
●​ Provides enterprise-grade features 
●​ Supports advanced data types (Arrays, JSON, JSONB) 
●​ Offers excellent documentation and community support 
●​ Has strong third-party tool support 

●​ Provides excellent data integrity guarantees 
Consequences 
Pros 
●​ Enterprise-grade features without licensing costs 
●​ Strong data integrity and ACID compliance 
●​ Rich ecosystem of tools and extensions 
●​ Excellent performance for complex queries 
●​ Support for modern data types and operations 
●​ Active community and regular updates 
Pros 
●​ Requires more initial setup compared to simpler databases 
●​ May need specialized knowledge for optimal performance 
●​ Higher learning curve for advanced features 
Sample Code 
 
-- Example of creating a table with advanced PostgreSQL features 
CREATE TABLE products ( 
    id SERIAL PRIMARY KEY, 
    name VARCHAR(255) NOT NULL, 
    description TEXT, 
    attributes JSONB, 
    tags TEXT[ ], 
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, 
    location GEOGRAPHY(POINT), 
    search_vector TSVECTOR 
); 
 
-- Example of using advanced features 
CREATE INDEX idx_products_search ON products USING GIN (search_vector); 
CREATE INDEX idx_products_attributes ON products USING GIN (attributes);
