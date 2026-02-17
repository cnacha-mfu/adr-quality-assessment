Azure Microsoft Cloud Computing Platform 
 
ADR 2: Using Azure Functions for Serverless Computing 
 
1. Context 
Our application requires a lightweight, event-driven compute platform to handle background 
tasks, webhook processing, and scheduled jobs. Running these tasks on virtual machines 
or Kubernetes clusters is expensive and inefficient. 
 
2. Decision 
We will use Azure Functions to execute lightweight tasks in response to HTTP requests, 
message queues, and scheduled events. 
 
3. Rationale 
We selected Azure Functions because: 
Serverless & Cost-Effective – Charges only for execution time, reducing costs. 
Auto-Scaling – Automatically scales based on incoming requests. 
Event-Driven Execution – Works with HTTP triggers, message queues, and timers. 
Seamless Integration – Connects with Azure Storage, Event Hubs, and Cosmos DB. 
Faster Development – Supports multiple languages (C#, JavaScript, Python, etc.). 
 
4. Pros and Cons 
Pros: 
 No infrastructure management required. 
 Auto-scales based on demand. 
 Integrates with Azure Services (Cosmos DB, Service Bus). 
 Supports multiple triggers (HTTP, queues, timers, etc.). 
 Pay-per-execution pricing saves costs. 
 
 Cons: 
 Cold start latency in Consumption Plan. 
 Limited execution time (5-minute timeout in Consumption Plan). 
 Less control over runtime environment than VMs or Kubernetes. 
 
 
 
 
 
 
 
 
 
 

                                Sample Code: Deploying an Azure Function 
 
Step 1: Install Azure Functions Core Tools 
 
npm install -g azure-functions-core-tools@4 --unsafe-perm true 
 
Step 2: Create and Deploy an Azure Function 
 
# Login to Azure CLI 
az login 
 
# Create a resource group 
az group create --name MyFunctionAppRG --location eastus 
 
# Create a storage account (required for Functions) 
az storage account create --name myfuncstorage --location eastus --resource-group 
MyFunctionAppRG --sku Standard_LRS 
 
# Create a function app 
az functionapp create --resource-group MyFunctionAppRG --consumption-plan-location 
eastus --runtime python --runtime-version 3.9 --functions-version 4 --name 
MyAzureFunction --storage-account myfuncstorage 
 
Step 3: Create a Simple HTTP Trigger Function 
 
import azure.functions as func 
import logging 
def main(req: func.HttpRequest) -> func.HttpResponse: 
    logging.info("Azure Function processed a request.") 
     
    name = req.params.get('name') 
    if not name: 
        try: 
            req_body = req.get_json() 
        except ValueError: 
            req_body = None 
        if req_body: 
            name = req_body.get('name') 
    if name: 
        return func.HttpResponse(f"Hello, {name}!") 
    else: 

        return func.HttpResponse("Please pass a name in the query string or request body.", 
status_code=400) 
 
 
    
Step 4: Deploy the Function 
 
# Deploy function to Azure 
func azure functionapp publish MyAzureFunction
