ADR (Architecture Decision Record ADR) 
 
Title 
The shift from monolithic architecture to microservices architecture 
Context 
Our existing systems were initially built on a monolithic architecture that 
was difficult to scale, maintain, and deploy efficiently. As our user base 
grew, we needed a solution that was more flexible and scalable to our 
needs. 
Decision 
We have decided to move from a monolithic architecture to a 
microservices architecture to improve scalability, maintainability, and 
deployment flexibility. 
Rationale 
Scalability 
●​ Allows independent scaling of services based on demand. 
 
Faster Deployment 
●​ Enables CI/CD(Continuous Integration / Continuous Deployment) 
pipelines for deploying services separately. 
 
Improved Maintainability 
●​ Each service has a smaller codebase, making it easier to 
manage. 
 
Technology Flexibility  
●​ Different microservices can use different languages and 
databases. 
Consequences 
Positive 
 
●​ Better resource utilization and performance. 
●​ Easier troubleshooting with service isolation. 
●​ Improved resilience by avoiding single points of failure. 
 
Negative 
●​ Increased complexity in managing inter-service communication. 
●​ Requires additional infrastructure for service discovery, API 
Gateway, and monitoring. 
 
 
 
 

Monolithic Approach (Before) 
A single service handling both users and orders: 
 
package main 
 
import ( 
    "encoding/json" 
    "net/http" 
) 
 
type User struct { 
    ID   int    `json:"id"` 
    Name string `json:"name"` 
} 
 
type Order struct { 
    OrderID int    `json:"order_id"` 
    User    User   `json:"user"` 
    Status  string `json:"status"` 
} 
 
func getOrder(w http.ResponseWriter, r *http.Request) { 
    user := User{ID: 1, Name: "John Doe"} 
    order := Order{OrderID: 101, User: user, Status: "Processing"} 
 
    w.Header().Set("Content-Type", "application/json") 
    json.NewEncoder(w).Encode(order) 
} 
 
func main() { 
    http.HandleFunc("/orders/101", getOrder) 
    http.ListenAndServe(":8080", nil) 
} 

 
Microservices Approach (After) 
Now, we split into User Service and Order Service. 
User Service (user-service/main.go) 
 
package main 
import ( 
    "encoding/json" 
    "net/http" 
) 
type User struct { 
    ID   int    `json:"id"` 
    Name string `json:"name"` 
} 
 
func getUser(w http.ResponseWriter, r *http.Request) { 
    user := User{ID: 1, Name: "John Doe"} 
    w.Header().Set("Content-Type", "application/json") 
    json.NewEncoder(w).Encode(user) 
} 
func main() { 
    http.HandleFunc("/users/1", getUser) 
    http.ListenAndServe(":8081", nil) 
} 
 
Order Service (order-service/main.go) 
package main 
 
import ( 
    "encoding/json" 
    "fmt" 
    "io/ioutil" 
    "net/http" 
) 
 
type User struct { 
    ID   int    `json:"id"` 
    Name string `json:"name"` 
} 
 
type Order struct { 
    OrderID int    `json:"order_id"` 
    User    User   `json:"user"` 
    Status  string `json:"status"` 
} 
 
func getOrder(w http.ResponseWriter, r *http.Request) { 
    resp, err := http.Get("http://localhost:8081/users/1") 
    if err != nil { 
        http.Error(w, "User service unavailable", 
http.StatusServiceUnavailable) 
        return 
    } 

    defer resp.Body.Close() 
 
    body, _ := ioutil.ReadAll(resp.Body) 
    var user User 
    json.Unmarshal(body, &user) 
 
    order := Order{OrderID: 101, User: user, Status: "Processing"} 
    w.Header().Set("Content-Type", "application/json") 
    json.NewEncoder(w).Encode(order) 
} 
 
func main() { 
    http.HandleFunc("/orders/101", getOrder) 
    fmt.Println("Order Service running on port 8082") 
    http.ListenAndServe(":8082", nil) 
}
