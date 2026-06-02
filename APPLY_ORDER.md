# Apply Order

1. Copy these files into the repository root.

2. Commit and push:

```bash
git add .
git commit -m "Add Argo CD GitOps deployment layer"
git push
```

3. Install infrastructure and Argo CD with Terraform:

```bash
terraform -chdir=infra/envs/gcp/dev init
terraform -chdir=infra/envs/gcp/dev apply
```

Use the matching cloud directory for AWS or Azure.

4. Apply Argo CD bootstrap manifests after Argo CD is installed:

```bash
kubectl apply -k argocd
```

5. After this, GitHub Actions updates image tags and Argo CD deploys the changed Kustomize overlays.

Do not run `kubectl apply -k k8s/services/...` manually for normal application releases once Argo CD owns the deployment.
