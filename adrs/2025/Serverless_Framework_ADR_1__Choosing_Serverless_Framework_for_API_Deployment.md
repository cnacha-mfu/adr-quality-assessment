Serverless Framework: Deployment & Management 
 ADR 1: Choosing Serverless Framework for API Deployment 
Context 
●​ Our development team is building a RESTful API that will serve thousands of users 
across different geographical locations.We need a scalable, cost-effective, and 
low-maintenance solution that can handle sudden traffic spikes without requiring 
manual scaling. 
Decision 
●​ We use Serverless Framework on AWS to deploy Lambda functions behind API 
Gateway. 
Rationale 
●​ Auto-scaling eliminates the need for server provisioning. 
●​ Pay-per-execution reduces operational costs. 
●​ Rapid iteration speeds up deployment & testing. 
Consequences 
Pros: 
●​ No server maintenance – Eliminates the need for provisioning and managing EC2 instances. 
●​ Seamless scalability – Automatically handles fluctuating traffic without downtime. 
●​ Integrated monitoring & logging – AWS CloudWatch and X-Ray provide insights into API 
performance. 
●​ Security & compliance – API Gateway supports authentication via IAM, Cognito, and JWT 
tokens. 
Cons: 
●​ Cold start latency – AWS Lambda experiences slight delays when invoked after inactivity. 
●​ Limited execution time – Lambda functions have a 15-minute timeout, which may not suit 
long-running tasks. 
●​ Complex debugging – Logs must be retrieved from AWS CloudWatch, requiring additional 
configuration. 
●​ Vendor lock-in – The application is deeply tied to AWS services, making migration to other 
platforms difficult. 

JavaScript
 
Sample Code 
 
service: my-serverless-app 
provider: 
  name: aws 
  runtime: nodejs18.x 
 
functions: 
  hello: 
    handler: handler.hello 
    events: 
      - http: 
          path: hello 
          method: get
