# Title 1
Adoption of ASP.NET Core for Mobile App Backend


## Context
We're developing a mobile app that requires a robust backend to handle user authentication, data storage, and business logic. We need to select a backend technology stack that aligns with our project requirements and team expertise.

## Decision
We have decided to adopt ASP.NET Core as the backend framework for our mobile app. ASP.NET Core provides a powerful and versatile platform for building scalable, high-performance web applications and APIs.

## Rationale
ASP.NET Core offers excellent performance and scalability, making it well-suited for handling the demands of our mobile app.
Our development team has extensive experience with C# and the .NET ecosystem, making ASP.NET Core a natural choice.
ASP.NET Core's built-in features, such as dependency injection, middleware pipeline, and Entity Framework Core for data access, streamline development and improve maintainability.


## Consequences
Pros:
Leveraging ASP.NET Core simplifies development by providing a unified platform for backend services.
Integration with Visual Studio and other Microsoft tools enhances developer productivity.
ASP.NET Core's cross-platform support allows for flexible deployment options.
Cons:
There may be a learning curve for team members who are not familiar with ASP.NET Core, but the long-term benefits outweigh this initial investment.


## Sample code
// Sample ASP.NET Core controller for handling user authentication

using Microsoft.AspNetCore.Mvc;

[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly IUserService _userService;

    public AuthController(IUserService userService)
    {
        _userService = userService;
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest request)
    {
        var user = _userService.Authenticate(request.Username, request.Password);
        if (user == null)
            return Unauthorized();

        // Generate JWT token
        var token = _userService.GenerateToken(user);
        return Ok(new { Token = token });
    }

    [HttpPost("register")]
    public IActionResult Register([FromBody] RegisterRequest request)
    {
        // Register new user
        var user = _userService.Register(request.Username, request.Password);
        if (user == null)
            return Conflict("Username already exists");

        // Generate JWT token
        var token = _userService.GenerateToken(user);
        return Ok(new { Token = token });
    }
}

