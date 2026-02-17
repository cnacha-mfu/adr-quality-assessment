ADR 2 : Using Prometheus for Alerting 
Title 
Prometheus for Alerting 
 
Context 
In addition to monitoring, we need a real-time alerting system that can detect anomalies (for 
example, CPU usage consistently above 80% or a sudden spike in API error rates). Our current 
setup does not provide flexible, real-time alerting, leading to delayed responses when issues 
occur. 
 
Decision 
We have decided to use Prometheus for alerting in conjunction with Alertmanager because: 
●​ We can define alerting rules directly in Prometheus (using PromQL to specify conditions) 
●​ It integrates with Alertmanager to send notifications through various channels like 
Slack, Email, or PagerDuty 
●​ It works seamlessly with our existing monitoring setup (Prometheus for Monitoring) 
 
Rationale 
●​ Integrated Alerting: Prometheus has built-in alerting capabilities, eliminating the need 
for an entirely separate tool 
●​ Flexible Configuration: Allows the creation of complex alert rules based on relevant 
metrics 
●​ Community Support: Numerous setup examples and best practices are available, 
thanks to a large user community 
 
Consequences 
Pros 

●​ Real-Time Alerts: Quick detection and resolution of issues, reducing downtime 
●​ Flexible Thresholds: Can easily configure CPU, Memory, Request Latency, Error Rate, 
etc. 
●​ Multi-Channel Notifications: Alertmanager supports Slack, Email, PagerDuty, and 
more 
Cons 
●​ Learning Curve: Requires knowledge of PromQL to write effective alerting rules 
●​ High Availability: If HA is needed for Alertmanager, multiple instances must be 
managed 
●​ Scalability: Large-scale environments with numerous metrics may require a more 
complex (distributed) architecture 
 
Sample Code 
# Example Alerting Rule: Trigger an alert when CPU usage exceeds 80% 
for 5 minutes 
 
groups: 
  - name: high_cpu_alerts 
    rules: 
      - alert: HighCPUUsage 
        expr: 100 - (avg by 
(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80 
        for: 5m 
        labels: 
          severity: critical 
        annotations: 
          summary: "High CPU usage on instance {{ $labels.instance }}" 
          description: "CPU usage is above 80% for more than 5 
minutes."
