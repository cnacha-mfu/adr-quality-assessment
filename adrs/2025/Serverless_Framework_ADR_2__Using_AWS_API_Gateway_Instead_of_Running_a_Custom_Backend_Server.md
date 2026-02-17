Serverless Framework: Deployment & Management 
 ADR 2: Using AWS API Gateway Instead of Running a Custom Backend 
Server 
Context 
●​ We need a scalable, cost-efficient way to expose APIs without managing servers. 
Running a backend on EC2 or Kubernetes adds complexity, requiring scaling, 
monitoring, and maintenance. A self-hosted solution also leads to unnecessary costs for 
idle resources. To simplify API management and reduce operational overhead, we chose 
AWS API Gateway, which provides auto-scaling, built-in security, and seamless AWS 
Lambda integration. 
Decision 
●​ We will use AWS API Gateway instead of a self-managed backend server to handle API 
requests and integrate it with AWS Lambda for processing. 
Rationale 
●​ Serverless & Scalable – API Gateway handles traffic spikes automatically. 
●​ Lower Cost – We pay only for API requests instead of running full-time servers. 
●​ Built-in Security & Throttling – AWS provides DDoS protection, request limits, and 
authentication via IAM or Cognito. 
●​ Seamless Integration – Connects easily with AWS Lambda, DynamoDB, and other 
AWS services.. 
Consequences 
Pros: 
●​ Eliminates the need for server maintenance. 
●​ Auto-scaling ensures performance even under high loads. 
●​ Pay-per-request pricing reduces operational costs. 
 
 
 

JavaScript
Cons: 
●​ Cold starts may introduce slight latency when invoking AWS Lambda. 
●​ Vendor lock-in – APIs are tied to AWS infrastructure. 
●​ Request limits – API Gateway enforces rate limits (default: 10,000 RPS per account) 
 
Sample Code 
 
service: my-api-service 
 
provider: 
  name: aws 
  runtime: nodejs18.x 
  region: us-east-1 
 
functions: 
  apiHandler: 
    handler: handler.api 
    events: 
      - http: 
          path: api 
          method: get 
          cors: true 
 
resources: 
  Resources: 
    ApiGatewayRestApi: 
      Type: AWS::ApiGateway::RestApi 
      Properties: 
        Name: MyServerlessAPI
