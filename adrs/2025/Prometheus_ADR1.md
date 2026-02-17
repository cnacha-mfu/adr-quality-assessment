ADR 1 : Using Prometheus for Monitoring 
Title 
Using Prometheus for Monitoring 
 
Context 
We currently use different tools to monitor our systems. This makes it hard to get a clear view of 
everything in one place. Some tools don’t give us enough details or alerts when problems 
happen. As our system grows, it’s becoming more difficult to manage and keep track of 
everything. We need a better way to monitor our systems that are easy to use and can develop 
with us. 
 
Decision 
We will use Prometheus to monitor our systems. Prometheus will collect data (like CPU usage 
and memory) from our servers, applications, and containers. It will check this data regularly and 
store it, so we can see trends over time. We will also use Grafana to create dashboards that 
show the data in an easy-to-read way. 
 
Rationale 
●​ All in One Place: Prometheus lets us see all our data in one dashboard. 
●​ Custom Metrics: We can track custom data that’s important for our business. 
●​ Scalable: Prometheus can handle a lot of data as our system grows. 
●​ Open Source and Popular: Prometheus is free to use and has a large community for 
support. 
●​ Good Alerts and Visualization: It works well with Alertmanager and Grafana for alerts 
and dashboards. 
 
Consequences 
Pros: 
●​ Unified View: We get a complete view of our system’s health in one place. 

●​ Custom Alerts: We can set alerts based on our own rules. 
●​ Easy to Scale: It can grow as our system grows. 
●​ Great Dashboards: Grafana gives us clear and interactive dashboards. 
Cons: 
●​ Setup Complexity: Setting up Prometheus and writing alert rules can be complicated. 
●​ Storage Limits: Prometheus stores data locally, so we need to plan for storage space. 
●​ Learning Curve: Our team needs to learn how to use PromQL (the query language for 
Prometheus). 
●​ Ongoing Maintenance: We need to regularly update and maintain Prometheus to keep 
it running smoothly. 
 
Sample Code 
1.​ Prometheus Configuration (prometheus.yml)​
This tells Prometheus where to get data from. 
 
global: 
  scrape_interval: 15s  # Check data every 15 seconds 
 
scrape_configs: 
  - job_name: 'node_exporter' 
    static_configs: 
      - targets: ['server1.local:9100', 'server2.local:9100'] 
 
  - job_name: 'application_metrics' 
    static_configs: 
      - targets: ['app1.local:8080', 'app2.local:8080'] 
    metrics_path: '/metrics' 
 
2.​ Alert Rule for High CPU Usage (alert.rules.yml)​
This alert rule checks if the CPU usage is above 80% for more than 5 minutes. 
groups: 
  - name: node_alerts 
    rules: 
      - alert: HighCPUUsage 

        expr: 100 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) 
by (instance) * 100 > 80 
        for: 5m 
        labels: 
          severity: critical 
        annotations: 
          summary: 'High CPU usage on {{ $labels.instance }}' 
          description: 'CPU usage is above 80% for more than 5 
minutes' 
 
3.​ Sample Code for Exposing Application Metrics (Python)​
This Python code collects metrics from an application and exposes them on port 8000. 
 
from prometheus_client import start_http_server, Summary, Counter 
import random 
import time 
 
# Create metrics to track 
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent 
processing request') 
ERROR_COUNT = Counter('error_count', 'Number of errors') 
 
@REQUEST_TIME.time() 
def process_request(): 
    """Simulate request processing""" 
    time.sleep(random.random()) 
    if random.random() > 0.9: 
        ERROR_COUNT.inc()  # Increment error count 
 
if __name__ == '__main__': 
    start_http_server(8000)  # Expose metrics on port 8000 
    while True: 
        process_request()
