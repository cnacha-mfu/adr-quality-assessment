ADR 2: Implementing Grafana Dashboards for System Health 
Monitoring 
 
Using Grafana Dashboards for System Performance and Health Monitoring 
 
We need a centralized monitoring solution to track system performance, including CPU, 
memory usage, API response times, and error rates. Having a customizable dashboard 
will help quickly identify bottlenecks and potential issues.  
 
What is the issue that we're seeing that is motivating this decision or change? 
- Monitoring system health requires accessing multiple logs and analytics tools.   
- There is no real-time, graphical representation of system performance.   
- Engineers must manually check performance metrics, leading to delays in issue 
detection.  
 
Decision 
We will implement Grafana dashboards with key system health metrics by integrating it 
with Prometheus for metric collection and Loki for log aggregation.   
 
Rationale 
- Centralized dashboards : One place for all system metrics and logs.   
- Interactive visualization : Supports graphs, heatmaps, and tables for easy analysis.   
- Flexible alerting : Set up alerts for CPU spikes, high memory usage, or API failures.   
- Customizable queries : Use “PromQL” and “LogQL” to filter and analyze logs 
efficiently.   
 
Consequences  
Pros: 
- Faster incident response time with real-time visualizations.   
- Improves system reliability and performance analysis.   
- Reduces dependency on manual log-checking.   
 
Cons: 
- Requires integration with “Prometheus” and “Loki”, increasing complexity.   
- Can consume significant resources if dashboards have too many queries.   
 
 
 
 

Sample Code  
Example “PromQL” query to track CPU usage in Grafana:   
 
promql 
rate(node_cpu_seconds_total{mode="user"}[5m]) 
 
 
Example “LogQL" query to filter errors from Loki logs:   
 
 
logql 
{app="my-service"} |= "error"
