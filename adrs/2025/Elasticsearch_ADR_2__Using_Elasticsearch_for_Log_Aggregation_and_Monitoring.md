Architecture Decision Record 
 
ADR 2 
 
Title: Using Elasticsearch for Log Aggregation and Monitoring 
 
Context 
In our system, managing logs from various application components is critical for 
debugging, performance monitoring, and security auditing. Traditional logging solutions 
often struggle with handling large log volumes efficiently, and querying logs in relational 
databases can be slow and resource-intensive. To ensure real-time log analysis and 
effective monitoring, we need a scalable and high-performance log aggregation 
solution. 
 
Elasticsearch, as part of the ELK (Elasticsearch, Logstash, Kibana) stack, provides an 
ideal solution for storing, indexing, and analyzing log data in real time. It supports 
structured and unstructured log data, allowing us to perform complex searches, 
aggregations, and visualizations easily. 
 
Decision 
We will integrate Elasticsearch as the central log storage and analytics engine in our 
logging system. The implementation steps include: 
●​ Configuring Logstash/Filebeat to collect logs from various sources and send 
them to Elasticsearch. 
●​ Setting up index lifecycle management to optimize storage and retention policies. 
●​ Implementing dashboards and alerts using Kibana for real-time monitoring. 
●​ Ensuring security measures like role-based access control and encrypted 
communication. 
 
Rationale 
1.​ Scalability: Elasticsearch supports horizontal scaling, allowing us to handle 
increasing log volumes efficiently. 
2.​ Real-Time Analysis: Enables near-instant log querying and visualization, 
reducing the time required for issue detection. 
3.​ Centralized Logging: Provides a unified platform for aggregating logs from 
multiple sources. 
4.​ Advanced Querying: Supports full-text search, filtering, and aggregations for 
better insights. 

5.​ Integration: Works seamlessly with Logstash and Kibana to create a complete 
observability solution. 
 
Consequences 
Pros: 
●​ Faster log searching and troubleshooting. 
●​ Scalable storage for handling large log volumes. 
●​ Real-time alerts and visualizations for proactive issue detection. 
●​ Integration with existing DevOps and security tools. 
 
Cons: 
●​ Requires additional infrastructure and maintenance. 
●​ Learning curve associated with Elasticsearch query DSL and index management. 
●​ Potential storage costs due to large-scale log indexing. 
 
Sample Code 
Sending Logs to Elasticsearch 
```python 
from elasticsearch import Elasticsearch 
import datetime 
 
es = Elasticsearch(["http://localhost:9200"]) 
 
log_entry = { 
    "timestamp": datetime.datetime.utcnow().isoformat(), 
    "level": "ERROR", 
    "message": "Application failed to connect to database" 
} 
 
es.index(index="logs", document=log_entry) 
 
Querying Logs in Elasticsearch 
python 
CopyEdit 
query = { 
    "query": { 
        "match": { 
            "level": "ERROR" 
        } 
    } 

} 
 
response = es.search(index="logs", body=query) 
print(response["hits"]["hits"])  # Output error logs
