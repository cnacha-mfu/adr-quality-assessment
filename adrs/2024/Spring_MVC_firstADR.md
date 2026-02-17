
# Title: Selecting Spring MVC as the Web Framework

# Context:
We have encountered manual configuration, tight coupling in codes, scability concerns and testing challenges in our previous web application development.

# Decision:
After careful consideration, we have decided to adopt Spring MVC as the web framework for our project.

# Rationale: Why do we choose this solution?
We choose Spring MVC for my web application because it offers a mature and well-supported framework with flexible configuration options and a clear separation of concerns through the MVC pattern. This makes our application maintainable, scalable, and secure, while also providing access to a wealth of resources and community support.

# Consequences
# Pros – What becomes easier?
It enables rapid and parallel development.
Development of the application becomes fast.
Easy for multiple developers to work together.
Easier to Update the application.
It is Easier to Debug because we have multiple levels in the application.
# Cons – What becomes more difficult?
Spring MVC has high complexity to develop the applications using this pattern.


# Sample Code:

Model class
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
Controller class
```
@Controller
public class HelloController {

    @GetMapping("/hello")
    public String hello(Model model) {
        Message message = new Message();
        message.setContent("Hello, World!");
        model.addAttribute("message", message);
        return "hello";
    }
}
```
View file
```html
<!DOCTYPE html>
<html>
<head>
    <title>Hello World</title>
</head>
<body>
    <h1 th:text="${message.content}"></h1>
</body>
</html>
```
In this example, when a request is made to "/hello", the hello() method in the HelloController class is invoked. It creates a Message object with the content "Hello, World!" and adds it to the model. The view file "hello.html" then renders this message. The ${message.content} syntax accesses the content of the Message object from the model.
