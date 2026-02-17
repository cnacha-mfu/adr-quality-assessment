ADR 1: Using Amazon EC2 for Scalable Compute Infrastructure 
 
Context 
Our application requires a high-performance, flexible, and scalable compute 
environment to handle dynamic workloads. Traditional on-premises servers limit 
scalability, require manual maintenance, and have high upfront costs. We need a 
cloud-based compute solution that allows us to provision and manage virtual 
servers on demand. 
 
Decision 
​
We choose Amazon EC2 (Elastic Compute Cloud) to host our applications and 
workloads instead of using on-premises servers or other managed compute solutions. 
 
Rationale 
●​ Scalability → Easily scale instances up or down based on demand. 
●​ Flexible Instance Types → Choose from various compute-optimized, 
memory-optimized, and GPU-based instances. 
●​ Security & Compliance → Integrated with AWS IAM, Security Groups, and 
VPC. 
●​ Customizable & Control → Full control over OS, software stack, and 
networking. 
●​ Cost-Effective → Various pricing models: On-Demand, Reserved, and Spot 
Instances. 
 
Consequences 
Cros 
●​ Supports a wide range of workloads, from web applications to machine learning 
models. 
●​ Provides full control over the environment, including OS and network 
configurations. 
●​ Easily integrates with AWS services like S3, RDS, and Lambda. 
 
Pros 
●​ Requires manual instance management unless automated with Auto Scaling or 
ECS. 
●​ Potential over-provisioning if not properly monitored. 
●​ Costs can increase if instances run continuously without optimization. 
 

 
Sample Code​
​
The sample code demonstrates how to create an EC2 instance using Python 
and Boto3 (the AWS SDK for Python). 
 
import boto3 
 
# Initialize EC2 client 
ec2 = boto3.client('ec2') 
 
# Launch EC2 instance 
response = ec2.run_instances( 
    ImageId='ami-0abcdef1234567890' # Replace with a valid AMIID 
    InstanceType='t2.micro',      # Free tier eligible instance 
    MinCount=1, 
    MaxCount=1, 
    KeyName='MyKeyPair',      # Replace with your Key Pair name 
    SecurityGroupIds=['sg-0123456789abcdef0'],  # Replace with 
your Security Group ID 
) 
 
# Print the instance ID of the created EC2 instance 
print("EC2 Instance Created:", 
response['Instances'][0]['InstanceId'])
