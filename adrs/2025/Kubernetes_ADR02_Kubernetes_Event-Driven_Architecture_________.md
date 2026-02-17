Event-Driven Architecture 
Context 
The system struggles to scale efficiently when there is a large number of users or 
events,and Managing multiple microservices in a distributed environment is complex 
and has limitations in scaling up or down the services. 
 
Decision 
Event Producers: Components that produce events, such as creating new data 
or changing status. 
Event Consumers: Components that consume and process events, such as 
sending notification emails or updating a database. 
 
Rationale 
Scalability: EDA allows the system to scale easily, particularly when adding or 
reducing the number of microservices handling events.​
 
Loose Coupling: EDA results in loose coupling between services, making it 
easier to develop and test components independently. 
 
Consequences 
Pros: 
●​ Scalability: The system can scale according to the volume of events occurring. 
Kubernetes and the message broker will handle this efficiently. 
●​ Flexibility: Adding or removing microservices responsible for event processing 
becomes easier. 
●​ Decoupling: Services will not be tightly coupled, allowing for easier development 
and testing. 
Cons: 
●​ Complexity: The system becomes more complex to design and maintain, such 
as configuring connections with the message broker and coordinating multiple 
microservices. 
●​ Debugging: Debugging a system with event communication between 
microservices may be more challenging, as there is no direct invocation between 
components. 
 
 
 
 
 

Sample code 
 
Event Producer (Sending Event) 
 
const { Kafka } = require('kafkajs') 
 
const kafka = new Kafka({ 
  clientId: 'my-app', 
  brokers: ['kafka-broker:9092'] 
}) 
 
const producer = kafka.producer() 
 
const sendEvent = async () => { 
  await producer.connect() 
  await producer.send({ 
    topic: 'user-creation', 
    messages: [ 
      { value: JSON.stringify({ userId: 123, email: 'user@example.com' }) } 
    ] 
  }) 
  console.log('Event sent') 
} 
 
sendEvent().catch(console.error)
