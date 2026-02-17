ADR 1: Implementing Security in Microservices Using the 
Spring Ecosystem 
Title 
Implementing Security in Microservices Using the Spring Ecosystem 
Context 
Security is a critical aspect of microservices architecture. Each microservice must 
ensure authentication, authorization, data encryption, and secure communication while 
maintaining scalability and flexibility. Implementing security in a distributed environment 
requires solutions that support token-based authentication, role-based access 
control (RBAC), API gateway security, and secure service-to-service 
communication. 
The system needs a framework that integrates security at multiple levels without 
excessive manual configuration. A secure microservices architecture should include: 
●​ Authentication and authorization using OAuth2 and JWT. 
●​ Secure API gateway management for request filtering and access control. 
●​ Secure service-to-service communication using mutual TLS (mTLS) and token 
propagation. 
●​ Centralized identity and access management to handle multiple services 
securely. 
Decision 
The Spring Ecosystem will be used to implement security in microservices due 
to its built-in support for authentication, authorization, and API security. Spring Security 
provides robust authentication and authorization mechanisms, including OAuth2 and 
JWT, ensuring secure access to APIs. Spring Cloud Gateway will handle API security 
and request validation, ensuring only authenticated requests reach microservices. 
Spring Security OAuth2 will be used for secure token exchange between services, 
and Spring Boot Actuator will monitor security-related events. 
Spring Boot’s native support for RBAC, security annotations, and token-based 
authentication ensures that services are protected without requiring extensive custom 
implementations. 

Rationale 
Several security frameworks were evaluated before selecting Spring Security 
and the Spring Ecosystem as the primary security solution. 
●​ Keycloak is an open-source identity and access management solution that 
provides OAuth2 and OpenID Connect but requires an external setup and 
maintenance. 
●​ Okta and Auth0 provide managed identity services but introduce vendor lock-in 
and additional costs. 
●​ Node.js (Passport.js) offers authentication solutions but lacks deep integration 
with microservices security patterns. 
●​ Spring Security was selected due to its seamless integration with Spring Boot 
and Spring Cloud, providing a complete security solution within the microservices 
ecosystem. 
Spring Security offers fine-grained access control through annotations 
(@PreAuthorize, @Secured), allowing microservices to enforce authorization rules 
efficiently. The combination of Spring Security, Spring Cloud Gateway, and OAuth2 
provides a scalable, robust, and cloud-ready security model for microservices. 
Consequences 
Pros 
●​ Provides built-in authentication and authorization through Spring Security. 
●​ Supports OAuth2, JWT, and token-based authentication for secure 
communication. 
●​ Seamless integration with Spring Cloud Gateway for securing API requests. 
●​ Offers RBAC and method-level security using annotations. 
●​ Compatible with Spring Boot Actuator for security monitoring and auditing. 
●​ Supports secure service-to-service communication with OAuth2 token 
propagation. 
Cons 
●​ Requires proper configuration to enforce security across multiple services. 
●​ OAuth2 and JWT setup can introduce initial complexity. 
●​ Increased latency in authentication requests due to token validation. 
 

Sample Code 
Spring Security OAuth2 Configuration 
@Configuration 
@EnableWebSecurity 
public class SecurityConfig { 
    @Bean 
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception { 
        http 
            .authorizeRequests(auth -> auth 
                .antMatchers("/public/**").permitAll() 
                .anyRequest().authenticated() 
            ) 
            .oauth2ResourceServer(OAuth2ResourceServerConfigurer::jwt); 
        return http.build(); 
    } 
} 
 
Spring Cloud Gateway Security Configuration 
spring: 
  cloud: 
    gateway: 
      routes: 
        - id: student-service 

          uri: lb://STUDENT-SERVICE 
          predicates: 
            - Path=/students/** 
          filters: 
            - TokenRelay= 
 
Role-Based Access Control (RBAC) using Spring Security Annotations 
@RestController 
@RequestMapping("/admin") 
public class AdminController { 
 
    @PreAuthorize("hasRole('ADMIN')") 
    @GetMapping("/dashboard") 
    public ResponseEntity<String> getAdminDashboard() { 
        return ResponseEntity.ok("Welcome to Admin Dashboard"); 
    } 
}
