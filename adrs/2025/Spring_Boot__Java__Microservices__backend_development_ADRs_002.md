ADR 2: Choosing Spring Boot for Cloud-Native 
Microservices Development 
Title 
Choosing Spring Boot for Cloud-Native Microservices Development 
Context 
In a cloud-native architecture, microservices need to be scalable, resilient, and 
portable across different cloud environments. A framework with built-in cloud-native 
support simplifies deployment, monitoring, and service management. The ideal 
framework should offer features such as service discovery, API gateways, 
centralized configuration, security, and observability without requiring extensive 
manual configurations. 
Several frameworks were considered, including Spring Boot, Quarkus, Micronaut, 
and Node.js (Express.js). Each framework provides different levels of cloud-native 
capabilities and integration with Kubernetes, service meshes, and cloud providers. 
Decision 
Spring Boot was selected as the primary framework for cloud-native 
microservices development due to its deep integration with Spring Cloud, Kubernetes, 
and cloud platforms such as AWS, Azure, and Google Cloud. It provides built-in tools for 
service discovery, centralized configuration, circuit breakers, and distributed 
tracing, making it a strong choice for large-scale cloud deployments. 
Spring Boot’s auto-configuration, dependency management, and compatibility with 
containerized environments(Docker, Kubernetes) make it more cloud-friendly than 
other frameworks. The ability to integrate seamlessly with cloud-native patterns 
reduces the complexity of managing distributed systems. 
Rationale 
Several frameworks were analyzed based on their cloud-native support and 
enterprise readiness. 
●​ Quarkus was considered due to its fast startup times and low memory 
consumption, making it efficient for cloud environments. However, it lacks mature 

built-in tools like Spring Cloud, requiring additional configurations for service 
discovery, resilience, and security. 
●​ Micronaut offers cloud-native features, including fast startup times and GraalVM 
support, but its ecosystem is not as mature as Spring Boot, and it lacks seamless 
integration with cloud services. 
●​ Node.js (Express.js) is lightweight and scalable but lacks built-in cloud-native 
support, requiring third-party libraries for essential microservices functionalities. 
●​ Spring Boot provides a comprehensive cloud-native ecosystem with Spring 
Cloud, Spring Security, Spring Data, and Kubernetes support, reducing the 
need for external dependencies. It is optimized for cloud-based deployments and 
integrates seamlessly with DevOps pipelines, service discovery tools, and 
monitoring frameworks. 
Consequences 
Pros 
●​ Provides built-in cloud-native features through Spring Cloud for service 
discovery, centralized configuration, and resilience. 
●​ Deep integration with Kubernetes for container orchestration and auto-scaling. 
●​ Supports Spring Boot Actuator, Prometheus, and distributed tracing 
(Zipkin/Sleuth) for cloud monitoring. 
●​ Enables secure microservices with Spring Security and OAuth2 
authentication. 
●​ Mature ecosystem with extensive documentation and enterprise support. 
Cons 
●​ Higher memory consumption compared to lightweight frameworks like Quarkus 
and Micronaut. 
●​ Steeper learning curve due to the large number of features and configurations. 
●​ More dependencies than minimalistic frameworks, increasing application size. 
 
 
 
 
 

Sample Code 
Spring Boot Kubernetes Integration Example 
spring: 
  application: 
    name: student-service 
  cloud: 
    kubernetes: 
      discovery: 
        enabled: true 
 
Spring Cloud Config Example for Centralized Configuration 
spring: 
  config: 
    import: "configserver:" 
  cloud: 
    config: 
      uri: http://config-server:8888 
      fail-fast: true
