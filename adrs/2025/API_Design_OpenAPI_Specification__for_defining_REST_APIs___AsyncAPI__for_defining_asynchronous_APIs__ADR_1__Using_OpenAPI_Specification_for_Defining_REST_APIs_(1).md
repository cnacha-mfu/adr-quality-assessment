ADR 1: Using OpenAPI Specification for Defining REST APIs 
Context​
Our project requires consistent and clear documentation for REST APIs. A standardized 
approach will ensure better collaboration, improve efficiency, and simplify integration with 
third-party services. 
Decision 
●​ Use OpenAPI Specification (OAS) for defining and documenting REST APIs. 
●​ Define API endpoints, request/response schemas, and error handling clearly using 
OpenAPI. 
●​ Integrate tools like Swagger UI for interactive documentation. 
●​ Enable automatic generation of client SDKs and server stubs from the OpenAPI 
definitions. 
Rationale 
●​ Recognized as the industry standard for RESTful API documentation. 
●​ Provides a structured and consistent approach to API definition. 
●​ Facilitates better collaboration between developers, testers, and stakeholders. 
●​ Enables automated testing, validation, and client code generation. 
Pros 
●​ Clear, standardized API documentation improves clarity and understanding. 
●​ Simplifies testing and validation through automated tools. 
●​ Enhances integration with third-party services through standardized contracts. 
●​ Boosts developer productivity by enabling code generation. 
Cons 
●​ Requires initial time and effort for setup and integration. 
●​ Needs to be consistently updated alongside code changes. 
●​ Limited to synchronous RESTful API communication. 
●​ May require additional tools for advanced validation features. 
○​  
 
 
 
 

Sample Code (FastAPI Example with OpenAPI) 
from fastapi import FastAPI 
from pydantic import BaseModel 
app = FastAPI() 
class Item(BaseModel): 
    name: str 
    price: float 
@app.post("/items/") 
async def create_item(item: Item): 
    return item
