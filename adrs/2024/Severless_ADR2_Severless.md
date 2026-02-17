# Title
Adoption of Serverless Framework for Cross-Platform Development
## Context
As our organization expands its cloud presence and adopts a multi-cloud strategy, we face challenges in managing and deploying serverless applications across various cloud platforms. Each cloud provider has its own set of tools, APIs, and deployment methodologies, leading to fragmentation and complexity in our development process. This fragmentation hampers agility and increases the learning curve for development teams.

## Decision
We propose adopting the Serverless Framework as the standard tool for cross-platform development of serverless applications. The Serverless Framework provides a unified abstraction layer that simplifies the development and deployment of serverless applications across multiple cloud providers. By standardizing on the Serverless Framework, we aim to streamline our development process, reduce vendor lock-in, and improve portability and maintainability of our applications.

## Rationale
We opt for the Serverless Framework due to its ability to provide a unified development experience across various cloud providers, ensuring a streamlined development process and reducing the learning curve. Additionally, its vendor-agnostic abstraction allows us to deploy functions seamlessly to different platforms, mitigating vendor lock-in and offering flexibility. Moreover, the rich ecosystem of plugins enhances productivity and efficiency by enabling customization and automation.

## Consequences
Pros:

-Simplified development with a consistent toolset and workflow.
-Enhanced portability and flexibility in deploying applications across multiple cloud platforms.
-Reduced risk of vendor lock-in, providing freedom to choose the most suitable cloud provider for each workload.

Cons:

-Initial setup and configuration may require learning and adjustment.
-Managing cross-platform deployments could demand additional expertise and coordination.
-Customization and extension of the framework may introduce complexity and maintenance overhead.

## Sample code

# serverless.yml

service: my-service

provider:
  name: aws
  runtime: nodejs14.x

functions:
  hello:
    handler: handler.hello
    events:
      - http:
          path: hello
          method: get


# javascript
// handler.js

module.exports.hello = async (event) => {
  return {
    statusCode: 200,
    body: JSON.stringify({
      message: 'Hello, world!'
    })
  };
};
