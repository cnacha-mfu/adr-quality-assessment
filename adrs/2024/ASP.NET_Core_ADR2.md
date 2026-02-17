# Title2
Integration of ASP.NET Core with Xamarin for Mobile App Development


## Context
We need to determine the frontend technology stack for our mobile app, considering factors such as performance, code sharing, and developer productivity.


## Decision
We have decided to integrate ASP.NET Core with Xamarin for developing the frontend of our mobile app. Xamarin allows us to build native mobile apps for iOS and Android using C#, providing a seamless and efficient development experience.

## Rationale

Xamarin facilitates code sharing between iOS and Android platforms, allowing us to maximize code reuse and minimize development effort.
Leveraging ASP.NET Core for the backend and Xamarin for the frontend promotes consistency and interoperability across the entire application stack.
Xamarin's performance is comparable to native development, ensuring that our mobile app meets the performance requirements of our users


## Consequences
Code sharing between iOS and Android platforms reduces development time and maintenance efforts.
Integration with Visual Studio and Xamarin.Forms simplifies UI development and testing.
Native performance and user experience are maintained, enhancing user satisfaction.
Cons:
Platform-specific features may still require platform-specific development and testing, although Xamarin provides tools and libraries to streamline this process.


## Sample code
// Sample Xamarin code for calling ASP.NET Core backend API

using System;
using System.Net.Http;
using System.Threading.Tasks;

public class ApiService
{
    private readonly HttpClient _httpClient;

    public ApiService()
    {
        _httpClient = new HttpClient();
        _httpClient.BaseAddress = new Uri("https://your-api-url.com/");
    }

    public async Task<string> LoginAsync(string username, string password)
    {
        var requestBody = new { Username = username, Password = password };
        var response = await _httpClient.PostAsJsonAsync("api/auth/login", requestBody);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsStringAsync();
    }

    public async Task<string> RegisterAsync(string username, string password)
    {
        var requestBody = new { Username = username, Password = password };
        var response = await _httpClient.PostAsJsonAsync("api/auth/register", requestBody);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsStringAsync();
    }
}

