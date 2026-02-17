Google Cloud Platform (GCP) 
 
Context 
Our project requires a website that processes and analyzes big data, supports future user 
growth, and provides reliable service. 
 
 
Decision  
Our team has decided to use Google Cloud Platform (GCP) as the cloud infrastructure for our  
website. 
 
 
Rationale 
1. Efficient data analysis: GCP provides the right tools for data analysis, such as Google 
Data Studio and Google Cloud Dataproc, that make it easy and fast to visualize and process 
large data sets while maintaining flexibility for customization and reporting, and outperform tools 
from AWS or Azure in some ways. 
2. Stability and durability: With services like Google Cloud Storage and Google Cloud 
Load Balancer, GCP provides a highly stable system that can withstand service disruptions 
smoothly, as well as automatic backups and load management, which makes infrastructure 
maintenance easier than competitors like AWS S3 and Azure Blob Storage. 
3. Big data management: GCP’s BigQuery enables fast and efficient big data analysis 
without the need to customize or manage hardware. GCP offers a more straightforward 
implementation than tools like Amazon Redshift or Azure Synapse Analytics when it comes to 
data management and integration. 
 
Consequences  
Pros 
1.​ Ease of setup and use:The Google Cloud Console has an easy-to-use and 
intuitive interface that makes it easy to quickly set up and manage services, 
especially when creating and scaling compute instances or storage services like 
Google Compute Engine or Google Cloud Storage. 
2.​ Comprehensive tools and services:GCP has tools available for big data analytics, 
such as BigQuery, that make it fast to process big data and queries without 
having to customize or manage additional hardware. It also has integrations with 
other services, such as Google Kubernetes Engine or Google Cloud Functions, 
that make it easy to scale and manage applications. 
3.​ Scalability:GCP’s infrastructure can be quickly and easily scaled using services 
like auto-scaling, which allows the system to automatically scale based on future 
user demand, allowing the project to grow without any problems. 

Cons 
1.​ Initial setup and service configuration:The initial setup of some services in GCP 
can be difficult for those without prior cloud experience, especially when working 
with complex services like Google Cloud Dataproc or BigQuery, which may 
require some customization and pre-configuration to get them working properly. 
2.​ Service Management and Integration:When multiple GCP services are used in 
the same project, such as compute, storage, and analytics services, it can be 
challenging to make these services work together smoothly and require some 
time to learn and integrate. 
3.​ Cost Management:Calculating and controlling costs in GCP can be difficult when 
the project is resource-intensive, especially for large-scale data processing or 
storage. This can require regular monitoring and tuning to prevent overruns. 
4.​ Team Training:GCP has a wide range of services and complex customization and 
configuration, so it can take some time for the development team to learn and 
train to use the services effectively. 
 
 
Sample code 
 
Create Instance Template 
gcloud compute instance-templates create my-instance-template \​
    --image-family debian-9 --image-project debian-cloud --machine-type 
f1-micro 
 
Create a Managed Instance Group 
gcloud compute instance-groups managed create my-instance-group \​
    --base-instance-name my-instance \​
    --template my-instance-template \​
    --size 1 \​
    --zone us-central1-a 
 
Set Auto Scaling: 
gcloud compute instance-groups managed set-autoscaling my-instance-group \​
    --max-num-replicas 10 \​
    --min-num-replicas 1 \​
    --target-cpu-utilization 0.6 \​
    --zone us-central1-a 
 
 

Check the scaling status: 
gcloud compute instance-groups managed describe my-instance-group --zone 
us-central1-a
