Microsoft Azure Cloud Computing Platform 
 
 
ADR 1: Using Azure Kubernetes Service (AKS) for Container Orchestration 
 
1. Context 
Our application follows a microservices architecture, and each service is containerized 
using Docker. To effectively manage and orchestrate these containers, we need a scalable 
and managed Kubernetes solution. 
 
2. Decision 
We will use Azure Kubernetes Service (AKS) to manage our containerized microservices, 
leveraging its scalability, security, and Azure ecosystem integration. 
 
3. Rationale 
We selected AKS because: 
Fully Managed Kubernetes – Microsoft handles upgrades, patches, and security. 
Seamless Azure Integration – Works with Azure DevOps, Azure AD, and Azure Monitor. 
Auto-Scaling & Load Balancing – Supports horizontal pod autoscaling (HPA). 
Security & Compliance – RBAC (Role-Based Access Control) and Azure AD Integration. 
Cost-Effective – Pay-as-you-go model with optimized resource allocation 
 
4. Pros and Cons 
Pros: 
 Simplifies Kubernetes cluster management. 
 Integrated with Azure DevOps for CI/CD automation. 
 Auto-scales during traffic spikes for high availability. 
 Built-in monitoring with Azure Monitor. 
 Supports hybrid cloud with Azure Arc. 
 
Cons: 
 Requires Kubernetes expertise for proper configuration. 
 Vendor lock-in with AKS-specific configurations. 
 Initial setup complexity with networking and RBAC policies. 
 
 
 
 
 
 
 
 
 

Sample code: 
 
Step 1: Set Up Azure and AKS Cluster 
 
# Login to Azure CLI 
az login 
 
# Create a resource group 
az group create --name MyResourceGroup --location eastus 
 
# Create an AKS cluster with 2 nodes 
az aks create --resource-group MyResourceGroup --name MyAKSCluster --node-count 2 
--enable-addons monitoring --generate-ssh-keys 
 
# Get Kubernetes credentials 
az aks get-credentials --resource-group MyResourceGroup --name MyAKSCluster 
 
Step 2: Deploy a Sample Application on AKS 
 
# Create a Kubernetes deployment 
kubectl create deployment my-app --image=mcr.microsoft.com/azuredocs/aks-helloworld:v1 
 
# Expose the deployment via LoadBalancer 
kubectl expose deployment my-app --type=LoadBalancer --port=80 
 
# Get the public IP of the service 
kubectl get service my-app 
 
Step 3: Enable Autoscaling for AKS 
 
# Enable Horizontal Pod Autoscaler (HPA) for dynamic scaling 
kubectl autoscale deployment my-app --cpu-percent=50 --min=2 --max=5 
 
# Verify the autoscaler 
kubectl get hpa
