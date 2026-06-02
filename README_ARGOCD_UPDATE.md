## Argo CD GitOps Deployment Layer

Argo CD fits between GitHub Actions and Kubernetes.

GitHub Actions builds and pushes container images.  
Argo CD deploys Kubernetes manifests from Git.  
Kubernetes runs the containers.  
Istio manages traffic between the running services.

```text
Developer pushes code
        ↓
GitHub Actions builds Docker image
        ↓
GitHub Actions pushes image to container registry
        ↓
GitHub Actions updates the Kustomize image tag in Git
        ↓
Argo CD detects the Git change
        ↓
Argo CD applies the correct Kustomize overlay
        ↓
Kubernetes rolls out new Pods
        ↓
Istio routes, secures, and observes service traffic
```

Argo CD does not replace Terraform, Docker, GitHub Actions, Kustomize, Kubernetes, or Istio.

It adds GitOps deployment control.

## Responsibility Split with Argo CD

```text
apps/
- Application source code
- Business logic
- Dockerfiles

.github/workflows/
- Builds container images
- Pushes images to the selected registry
- Updates Kustomize image tags in Git

k8s/
- Kubernetes desired state
- Istio service manifests
- Kustomize bases and overlays

argocd/
- Argo CD AppProject definitions
- Argo CD Application definitions
- Argo CD ApplicationSet definitions

infra/
- Terraform cloud infrastructure
- Kubernetes cluster creation
- Registry creation
- Istio installation
- Argo CD installation
```

## Why Argo CD Is Useful with Many Microservices

With hundreds of microservices, manual deployment becomes fragile.

Without Argo CD:

```text
500 services
500 image updates
500 possible kubectl apply targets
No clean drift detection
No central sync visibility
Harder rollback tracking
```

With Argo CD:

```text
500 services defined in Git
Cluster state continuously compared against Git
Per-service sync status
Per-service rollout visibility
Manual or automatic sync
Rollback through Git history
Less direct kubectl usage
```

## Updated Deployment Flow

```text
Application source code
        ↓
Docker build
        ↓
Container registry push
        ↓
GitHub Actions updates Kustomize image tag
        ↓
Git commit to deployment manifests
        ↓
Argo CD detects Git change
        ↓
Argo CD applies Kustomize overlay
        ↓
Kubernetes Deployment starts Pods
        ↓
Kubernetes Service provides stable DNS
        ↓
Istio routes, secures, and observes traffic
```

## GitHub Actions and Argo CD

GitHub Actions should not run `kubectl apply` in this model.

GitHub Actions should:

- Build the container image
- Push the container image to the registry
- Update the correct Kustomize overlay image tag
- Commit the manifest change back to Git

Argo CD should:

- Watch the Git repository
- Detect changes under `k8s/`
- Apply the correct Kustomize overlay
- Reconcile drift if the live cluster differs from Git

## Image Tag Update Rule

After GitHub Actions builds an image, Kubernetes must know the new image tag.

Bad model:

```text
GitHub Actions builds checkout:abc123
Kustomize still says checkout:oldtag
Argo CD sees no Git change
Nothing deploys
```

Correct model:

```text
GitHub Actions builds checkout:abc123
GitHub Actions updates newTag to abc123
GitHub Actions commits the Kustomize change
Argo CD sees the Git change
Argo CD deploys checkout:abc123
```

Example Kustomize image block:

```yaml
images:
  - name: checkout-image
    newName: us-docker.pkg.dev/PROJECT_ID/apps/checkout
    newTag: abc123
```

## New Repository Additions

Add this structure:

```text
argocd/
├── kustomization.yaml
├── projects/
│   └── apps-project.yaml
├── applications/
│   ├── platform-gcp.yaml
│   ├── platform-aws.yaml
│   └── platform-azure.yaml
└── applicationsets/
    ├── services-gcp.yaml
    ├── services-aws.yaml
    └── services-azure.yaml

infra/
└── modules/
    └── argocd/
        ├── main.tf
        └── variables.tf

scripts/
└── update-image-tag.py

.github/
└── workflows/
    ├── build-and-update-gcp.yml
    ├── build-and-update-aws.yml
    └── build-and-update-azure.yml
```

## Argo CD Sync Model

Platform resources are deployed once per cloud:

```text
k8s/platform
```

Service resources are deployed one service at a time through ApplicationSets:

```text
k8s/services/checkout/overlays/gcp
k8s/services/payment/overlays/gcp
k8s/services/inventory/overlays/gcp
k8s/services/user/overlays/gcp
```

For AWS:

```text
k8s/services/<service>/overlays/aws
```

For Azure:

```text
k8s/services/<service>/overlays/azure
```

## Final Rule

```text
GitHub Actions builds containers.
GitHub Actions updates Kustomize image tags.
Argo CD deploys Kubernetes manifests from Git.
Kustomize selects the correct image.
Kubernetes runs the containers.
Istio manages service traffic.
```
