# Cloud Agnostic Kubernetes Deployment

Cloud-agnostic Kubernetes deployment scaffold for GCP, AWS, and Azure using Terraform, Kubernetes, Istio, Helm, and Kustomize.

This repository is designed for many microservices. The sample services are:

- `checkout`
- `payment`
- `inventory`
- `user`

The same pattern scales to hundreds of services.

## Core Model

```text
Container image = packaging unit
Pod = runtime unit
Deployment = rollout and scaling unit
Service = stable network identity
Istio = service-to-service traffic, security, and observability layer
Business logic = application code and domain boundaries
```

Istio does not split business logic from the application. Microservice boundaries split business logic. Istio manages communication, security, traffic policy, and observability between services.

## Repository Layout

```text
repo/
├── .github/
│   └── workflows/
│       ├── build-gcp.yml
│       ├── build-aws.yml
│       └── build-azure.yml
├── apps/
│   ├── checkout/
│   ├── payment/
│   ├── inventory/
│   └── user/
├── infra/
│   ├── modules/
│   │   ├── gke/
│   │   ├── eks/
│   │   ├── aks/
│   │   └── istio/
│   └── envs/
│       ├── gcp/dev/
│       ├── aws/dev/
│       └── azure/dev/
├── k8s/
│   ├── platform/
│   │   ├── namespaces/
│   │   ├── ingress/
│   │   ├── istio-policies/
│   │   └── kustomization.yaml
│   └── services/
│       ├── checkout/
│       ├── payment/
│       ├── inventory/
│       └── user/
├── scripts/
├── services.txt
├── Makefile
└── README.md
```

## 500 Microservices Deployment Model

With hundreds of microservices, the deployment model must be service-based.

Do not use one huge Kubernetes `Deployment` for all services.

Bad:

```text
One Deployment with 500 containers
```

Correct:

```text
500 Deployments, each independently scalable and releasable
```

Each microservice should normally own:

- Application source code
- Dockerfile
- Container image
- Kubernetes Deployment
- Kubernetes Service
- Kubernetes ServiceAccount
- ConfigMap and Secret references
- HPA
- PodDisruptionBudget
- Istio DestinationRule
- Optional Istio AuthorizationPolicy
- Optional Istio VirtualService if externally exposed

## Infrastructure vs Application Split

Terraform owns:

- GKE, EKS, or AKS cluster creation
- Container registries
- Cloud workload identity setup
- Node pools
- IAM plumbing
- Istio Helm installation

Kustomize owns:

- Kubernetes Deployments
- Services
- ServiceAccounts
- HPAs
- PDBs
- Istio routing policies
- Cloud-specific Kubernetes patches

Application code owns:

- Business logic
- API contracts
- Runtime behavior
- Service boundaries

Istio owns:

- mTLS
- Traffic routing
- Retries
- Timeouts
- Circuit breaking
- Canary routing
- Authorization policies
- Observability
- Ingress and egress control

## Container Registry Patterns

### Option 1: Separate Registry per Cloud

| Cloud | Registry |
|---|---|
| GCP | Artifact Registry |
| AWS | Elastic Container Registry |
| Azure | Azure Container Registry |

Example image paths:

```text
GCP:
europe-west1-docker.pkg.dev/PROJECT_ID/apps/checkout:v1.0.0

AWS:
ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/checkout:v1.0.0

Azure:
ACR_NAME.azurecr.io/checkout:v1.0.0
```

### Option 2: One Shared Registry

```text
ghcr.io/YOUR_ORG/checkout:v1.0.0
docker.io/YOUR_ORG/checkout:v1.0.0
```

## Deployment Flow

```text
Application source code
 ↓
Docker build
 ↓
Container registry push
 ↓
Kustomize overlay selects image
 ↓
Kubernetes Deployment starts Pods
 ↓
Kubernetes Service provides stable DNS
 ↓
Istio routes, secures, and observes traffic
```

## Traffic Flow

```text
User
 ↓
Cloud Load Balancer
 ↓
Istio Ingress Gateway
 ↓
Istio Gateway
 ↓
Istio VirtualService
 ↓
Kubernetes Service
 ↓
Pod
 ↓
Container
```

## Create Infrastructure

### GCP

```bash
cp infra/envs/gcp/dev/terraform.tfvars.example infra/envs/gcp/dev/terraform.tfvars
terraform -chdir=infra/envs/gcp/dev init
terraform -chdir=infra/envs/gcp/dev apply
```

Get cluster credentials:

```bash
gcloud container clusters get-credentials cloud-agnostic-dev \
  --region europe-west1 \
  --project PROJECT_ID
```

### AWS

```bash
cp infra/envs/aws/dev/terraform.tfvars.example infra/envs/aws/dev/terraform.tfvars
terraform -chdir=infra/envs/aws/dev init
terraform -chdir=infra/envs/aws/dev apply
```

Get cluster credentials:

```bash
aws eks update-kubeconfig \
  --region eu-west-1 \
  --name cloud-agnostic-dev
```

### Azure

```bash
cp infra/envs/azure/dev/terraform.tfvars.example infra/envs/azure/dev/terraform.tfvars
terraform -chdir=infra/envs/azure/dev init
terraform -chdir=infra/envs/azure/dev apply
```

Get cluster credentials:

```bash
az aks get-credentials \
  --resource-group rg-cloud-agnostic-dev \
  --name cloud-agnostic-dev
```

## Deploy Platform Resources

```bash
kubectl apply -k k8s/platform
```

This applies:

- `apps` namespace
- Istio injection label
- shared public Istio Gateway
- public VirtualService routes
- strict mTLS policy

## Build and Deploy One Service

### GCP

```bash
PROJECT_ID=your-project-id TAG=v1.0.0 ./scripts/build-push.sh gcp checkout
./scripts/deploy-service.sh gcp checkout
```

### AWS

```bash
ACCOUNT_ID=123456789012 REGION=eu-west-1 TAG=v1.0.0 ./scripts/build-push.sh aws checkout
./scripts/deploy-service.sh aws checkout
```

### Azure

```bash
ACR_NAME=myregistry TAG=v1.0.0 ./scripts/build-push.sh azure checkout
./scripts/deploy-service.sh azure checkout
```

## Deploy All Sample Services

```bash
./scripts/deploy-all.sh gcp
./scripts/deploy-all.sh aws
./scripts/deploy-all.sh azure
```

## Generate a New Microservice

```bash
./scripts/create-service.py orders
```

This creates:

```text
apps/orders/
k8s/services/orders/base/
k8s/services/orders/overlays/gcp/
k8s/services/orders/overlays/aws/
k8s/services/orders/overlays/azure/
```

Then add the new service to:

```text
services.txt
```

## Local Build Example

```bash
docker build -t checkout:local ./apps/checkout
docker run --rm -p 8080:8080 checkout:local
curl http://localhost:8080/health
```

## Service-to-Service Calls

Internal Kubernetes DNS format:

```text
http://payment.apps.svc.cluster.local
http://inventory.apps.svc.cluster.local
http://user.apps.svc.cluster.local
```

For services in the same namespace, short DNS names also work:

```text
http://payment
http://inventory
http://user
```

## Istio Public Routing

The platform exposes sample public routes:

```text
/checkout → checkout service
/user     → user service
```

Internal services such as `payment` and `inventory` do not need public ingress routes unless required.

## Large Mesh Rule

For many services:

```text
Application code owns business logic.
Docker packages each service.
Kubernetes runs each service.
Kustomize keeps service manifests reusable across clouds.
Terraform creates the cloud infrastructure.
Istio manages traffic, security, and observability between services.
```
