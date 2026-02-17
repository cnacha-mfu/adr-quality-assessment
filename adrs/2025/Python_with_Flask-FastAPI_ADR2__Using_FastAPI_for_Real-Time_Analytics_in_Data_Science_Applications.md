ADR2: Using FastAPI for Real-Time Analytics in Data Science Applications 
Context 
Our project involves building a real-time analytics system that can process and respond to data 
inputs continuously and in real-time. This system needs to handle high volumes of data 
efficiently, perform data validation, and ensure timely responses. Given these requirements, the 
choice of web framework is crucial to the success of the project. 
Decision 
We will use FastAPI for our real-time analytics system due to its asynchronous capabilities, 
performance benefits, and ease of integrating real-time data processing tools. 
Rationale 
●​ Asynchronous Programming: FastAPI's support for asynchronous programming 
allows handling numerous data streams concurrently. This is essential for real-time data 
processing where delays in data handling can lead to bottlenecks. 
●​ Performance: FastAPI is one of the fastest web frameworks for Python, crucial for 
real-time analytics where processing speed is a key concern. 
●​ Scalability: Its ability to handle large numbers of simultaneous connections with minimal 
overhead makes it ideal for scaling up as the data volume or the number of users 
increases. 
●​ Data Validation: Built-in support for Pydantic means that data can be validated and 
serialized efficiently, reducing errors and ensuring that the data conforms to expected 
formats. 
●​ Ease of Maintenance: FastAPI’s automatic interactive API documentation helps 
maintain clear documentation, which is vital for long-term maintenance and scalability of 
software projects. 
Consequences 
●​ Pros: 
○​ Improved handling of concurrent data streams reduces latency in data 
processing, enhancing the ability to perform analytics in real time. 
○​ Scalability features allow the system to grow without significant changes to the 
infrastructure. 
○​ Automatic documentation and schema validation features streamline 
development and reduce bugs. 
●​ Cons: 
○​ The asynchronous model might require developers to have or gain a specific skill 
set, potentially steepening the learning curve. 

○​ Being a relatively new framework, some libraries or tools may not yet be fully 
adapted for use with FastAPI. 
 
from fastapi import FastAPI, WebSocket 
from pydantic import BaseModel 
 
app = FastAPI() 
 
class DataStream(BaseModel): 
   timestamp: float 
   value: float 
 
@app.websocket("/ws") 
async def websocket_endpoint(websocket: WebSocket): 
   await websocket.accept() 
   while True: 
       data = await websocket.receive_json() 
       data_stream = DataStream(**data) 
       # Process the incoming data stream 
       await process_data(data_stream) 
       await websocket.send_text(f"Received data at 
{data_stream.timestamp} with value {data_stream.value}") 
 
async def process_data(data: DataStream): 
   # Implement real-time data processing logic here 
   pass 
 
if __name__ == "__main__": 
   import uvicorn 
   uvicorn.run(app, host="0.0.0.0", port=8000)
