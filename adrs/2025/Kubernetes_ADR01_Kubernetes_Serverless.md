Serverless 
 
Context 
Managing servers leads to high costs during idle times, And we need to handle 
scaling when there is a heavy load. 
 
Decision 
Use KNative for managing functions running on Kubernetes.Serverless 
architecture will enable automatic scaling and stop functions when not in use. 
 
Rationale 
Cost savings: Pay only for actual function usage (pay-as-you-go). 
Automatic scaling: The system can automatically handle increasing workloads. 
Reduced system maintenance: No need to manage servers or deal with the 
complexities of scaling. 
 
Consequences 
Pros: 
●​ Cost reduction: You pay only when the function is in use, without maintaining 
idle servers. 
●​ Easy scaling: The system can automatically increase or decrease processing 
power. 
●​ Easier development: No need to worry about server setup or resource 
management. 
Cons: 
●​ Cold start delays: Sometimes, the function startup might be slow, particularly if 
the server has been idle. 
●​ Limited control: You may not have full control over resource management 
details, such as boot times or container runtime. 
 
 
 
 
 
 
 
 
 

Sample code 
 
Sample AWS Lambda Function in Node.js 
exports.handler = async (event) => { 
    console.log("Request received:", event); 
    return { 
        statusCode: 200, 
        body: JSON.stringify({ message: "Hello, Serverless!" }), 
    }; 
};
