ADR. Google Cloud Platform (GCP) 
 
Context 
Our project requires a website that runs on Google’s global infrastructure network, enabling 
stable communication between servers and services while ensuring security in service usage. 
 
Decision  
Our team has decided to use Google Cloud Platform (GCP) due to its services that make 
application scaling easier, such as Cloud Run and Google Kubernetes Engine (GKE). 
 
Rationale 
1.​ Global Network and Access: Google Cloud Platform (GCP) is a network that uses 
Google's Software-Defined Networking (SDN) and global infrastructure, which reduces 
latency and increases network efficiency. It supports Global Load Balancer, which can 
distribute traffic across regions without using DNS Routing. It has a Private Google 
Access system that allows VMs within a VPC to access Google APIs without having to 
go through the Internet. 
2.​ Security and Compliance: It has built-in security features such as IAM, VPC Service 
Controls, and Cloud Security Command Center. It has VPC Service Controls to prevent 
data leakage from Google services such as BigQuery, Cloud Storage, and supports 
DDoS Protection and Cloud Armor to protect against network attacks. 
3.​ Strong Support for DevOps and CI/CD: GCP has tools for continuous development and 
deployment of code, such as Cloud Build, Cloud Deploy, and Artifact Registry, which 
help to set up CI/CD Pipelines efficiently. 
 
 
Consequences  
 
Pros 
1.​ Low Latency Using Google's network of data centers around the world, it can reduce 
latency and improve application performance. 
2.​ High security Supports Firewall, Private Google Access and Identity-Aware Proxy (IAP) 
to protect against cyber threats and restrict unauthorized user access. 
3.​ Automatic scaling The network system can adjust to suit the increasing load as the 
system needs. 
4.​ Supports Multi-Cloud and Hybrid Cloud Can connect to AWS or Azure via Cloud 
Interconnect and Anthos, allowing businesses to take advantage of multiple clouds 
together. 
5.​ AI and Big Data tools Support Vertex AI, BigQuery and Dataflow for AI, Machine 
Learning and Big Data tasks, allowing organizations to analyze large data and develop 
AI models efficiently. 
 
 

 
 
 
Cons  
1.​ Complexity in Configuration GCP has a global VPC concept, which is different from other 
cloud providers such as AWS that use VPCs separated by region. This may take time for 
teams familiar with AWS to learn and adapt, and setting up firewalls, load balancers, and 
private networking can require a lot of expertise. 
2.​ Multi-Cloud Limitations Although GCP supports hybrid clouds and multi-clouds via 
Anthos and Cloud Interconnect, cross-cloud setup can be more complex than AWS or 
Azure. 
3.​ Regional Availability & Restrictions Some GCP services are not available in all regions, 
forcing some organizations to choose regions that may not be suitable for their business. 
4.​ Support & Documentation Challenges GCP's technical support may not be as 
comprehensive as AWS and Azure, especially the free tier. 
 
 
Sample code 
Create a new VPC 
gcloud compute networks create my-vpc --subnet-mode=custom 
Create Subnet 
gcloud compute networks subnets create my-subnet \ 
  --network=my-vpc \ 
  --region=us-central1 \ 
  --range=10.0.1.0/24 
Create a Firewall Rule to allow SSH access 
gcloud compute firewall-rules create allow-ssh \ 
  --network=my-vpc \ 
  --allow=tcp:22 \ 
  --source-ranges=0.0.0.0/0 \ 
  --target-tags=ssh-access
