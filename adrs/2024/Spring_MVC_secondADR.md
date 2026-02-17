# Title: Introducing RESTful API with Spring MVC

# Context:
Our application needs to expose its functionality via a web API to allow integration with external systems or client applications. We need a robust and scalable solution to implement RESTful APIs that adhere to best practices and industry standards.

# Decision:
After thorough consideration, we have opted to utilize PostgreSQL as the primary database engine for our We propose extending our Spring MVC application to include RESTful API endpoints using Spring's support for building RESTful web services. This involves creating dedicated controllers to handle HTTP requests and responses in a RESTful manner, utilizing annotations such as @RestController, @GetMapping, @PostMapping, etc.

# Rationale:
Scalability: Spring MVC's modular architecture and support for asynchronous processing allow us to build scalable and high-performance RESTful APIs capable of handling a large number of concurrent requests.

# Consequences

# Pros:

Integration: Spring MVC seamlessly integrates with other components of the Spring ecosystem, allowing us to leverage additional features such as security, data access, and dependency injection.

# Cons:


API Versioning: Managing API versioning and backward compatibility can be challenging, requiring careful planning and implementation to avoid breaking changes.

# Sample Code:
Model
```java
public class Message {
    private String content;

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }
}
```
Controller
```java
@RestController
@RequestMapping("/api")
public class ApiController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello, World!";
    }

    @PostMapping("/echo")
    public String echo(@RequestBody String message) {
        return message;
    }
}
```
View
```java
<!DOCTYPE html>
<html>
<head>
    <title>Hello Page</title>
</head>
<body>
    <h1>Hello Page</h1>
    <p th:text="${message.content}"></p>
</body>
</html>
```
In this example, the ApiController defines two endpoints: /api/hello for handling GET requests and /api/echo for handling POST requests. The @RestController annotation indicates that this class is a RESTful controller, and the @GetMapping and @PostMapping annotations specify the HTTP methods for the corresponding endpoints.
        
