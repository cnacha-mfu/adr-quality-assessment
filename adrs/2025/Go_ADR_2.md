ADR (Architecture Decision Record ADR) 
 
Title 
Migrating from Python to Go for E-commerce Microservices 
Context 
Our E-commerce system needs to handle a high volume of orders, 
especially during sales campaigns, where thousands of transactions 
occur per second. The existing system, built with Python + Django, 
struggles with high latency and high resource consumption (CPU & 
memory usage), creating performance bottlenecks and making scaling 
difficult. 
Decision 
The development team has decided to migrate key microservices from 
Python to Go to improve performance and scalability. 
Rationale 
Improved Performance 
●​ - Go is a compiled language, making execution significantly faster 
than Python. 
 
Better Concurrency Handling 
●​ - Using Goroutines and Channels instead of traditional threads 
allows efficient parallel order processing. 
 
Reduced API Latency 
●​ - Switching from REST API to gRPC enables faster data 
transmission and lower bandwidth usage. 
 
Easier Scalability 
●​ - Go’s lightweight nature reduces CPU & RAM consumption, 
making horizontal scaling more efficient. 
Consequences 
Positive 
●​ - Reduced API latency from 500ms → 50ms 
●​ - 40% lower memory (RAM) usage 
●​ - 3x more transaction throughput compared to Python 
●​ - Fewer servers needed, leading to cost savings 
 
Negative 
●​ - Developers need to learn Go and gRPC 
●​ - Monitoring & debugging tools must be adjusted for the new 
Go-based stack 
 
 
 

Sample code Phyton(Before Migration) 
from flask import Flask   
import time   
   
app = Flask(__name__)   
 
@app.route('/process')   
def process_request():   
    time.sleep(2)     
    return "Processed", 200   
   
if __name__ == "__main__":   
    app.run(host="0.0.0.0", port=5000)   
 
Sample Code Go(After Migration) 
//When you created project finish 
package main   
   
import (   
    "fmt"   
    "net/http"   
    "time"   
)   
   
func processHandler(w http.ResponseWriter, r *http.Request) {   
    time.Sleep(2 * time.Second)   
    fmt.Fprintln(w, "Processed")   
}   
   
func main() {   
    http.HandleFunc("/process", processHandler)   
    http.ListenAndServe(":5000", nil)   
}
