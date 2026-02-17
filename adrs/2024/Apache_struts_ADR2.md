## Architecture Decision Record (ADR) 2- Migration from Apache Struts to Spring Boot


## Context
We are experiencing security vulnerabilities and protection demanding situations with our contemporary framework, Apache Struts. The recent security breaches and the cease-of-life statement for Struts 1.X variations have prompted us to reevaluate our technology stack.


## Decision
We will migrate our application from Apache Struts to Spring Boot.


## Rationale
Spring Boot gives a contemporary, strong, and actively maintained framework with integrated security capabilities. Its extensive network help and common updates make sure timely worm fixes and security patches. By migrating to Spring Boot, we can future-proof our utility and mitigate the risks related to using an outdated framework like Apache Struts.

## Consequences
Pros:
Enhanced Security:Spring Boot gives comprehensive protection functions inclusive of authentication, authorization, and encryption, decreasing the risk of security breaches.
Simplified Development: Spring Boot's convention-over-configuration technique and integrated dependencies streamline improvement, resulting in quicker shipping of features.
Better Performance: Spring Boot's light-weight field and efficient aid utilization make a contribution to advanced utility performance.
Ecosystem Integration: Spring Boot seamlessly integrates with different Spring initiatives and 0.33-party libraries, enabling simpler adoption of recent technology and tools.

Cons:Learning Curve: Team participants unfamiliar with Spring Boot may additionally require schooling to ramp up their skills, doubtlessly leading to a temporary productivity dip.
Migration Effort: Migrating existing codebase and configurations from Apache Struts to Spring Boot would require time and effort, specially for complicated packages.
Potential Disruption: The migration process may additionally briefly disrupt ordinary development and deployment activities, impacting mission timelines.


## Sample code
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello, Spring Boot!";
    }
}

