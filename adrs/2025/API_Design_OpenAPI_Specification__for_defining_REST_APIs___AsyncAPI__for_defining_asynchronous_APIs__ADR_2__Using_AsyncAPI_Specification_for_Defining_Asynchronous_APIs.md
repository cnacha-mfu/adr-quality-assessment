ADR 2: Using AsyncAPI Specification for Defining Asynchronous APIs 
Context​
Our system requires asynchronous, event-driven communication using protocols like 
WebSockets. A consistent approach to defining asynchronous APIs is necessary for scalability 
and maintainability. 
Decision 
●​ Use AsyncAPI Specification to document all asynchronous APIs. 
●​ Define message channels, payloads, and events using AsyncAPI format. 
●​ Leverage built-in tools for message format validation. 
●​ Integrate message simulation tools for testing event flows. 
Rationale 
●​ Specifically designed for event-driven, asynchronous systems. 
●​ Provides clear and structured documentation for messaging protocols. 
●​ Supports scalability across microservices architectures. 
●​ Enhances system reliability by clearly defining message flows and payloads. 
Pros 
●​ Simplifies documentation for complex asynchronous communication. 
●​ Supports various protocols like Kafka, MQTT, and WebSockets. 
●​ Encourages scalable and modular system design. 
●​ Improves team collaboration with well-defined communication channels. 
Cons 
●​ Requires developers to learn the AsyncAPI specification and tools. 
●​ Documentation needs ongoing updates to remain accurate. 
●​ Fewer tools and integrations compared to OpenAPI. 
●​ Requires additional testing infrastructure for asynchronous message simulation. 
 
 
 
 
 
 

Sample Code (WebSocket Example) 
 
from fastapi import FastAPI, WebSocket, WebSocketDisconnect 
 
app = FastAPI() 
 
# Active connections set 
active_connections = set() 
 
# WebSocket endpoint for real-time communication 
@app.websocket("/ws") 
async def websocket_endpoint(websocket: WebSocket): 
    await websocket.accept() 
    active_connections.add(websocket) 
    try: 
        while True: 
            data = await websocket.receive_text() 
            # Broadcast message to all connected clients 
            for connection in active_connections: 
                await connection.send_text(f"Broadcast: {data}") 
    except WebSocketDisconnect: 
        active_connections.remove(websocket)
