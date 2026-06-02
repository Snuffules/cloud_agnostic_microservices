variable "argocd_chart_version" {
  description = "Optional argo-cd Helm chart version. Leave null to use the latest chart available at install time."
  type        = string
  default     = null
}

module "argocd" {
  source = "../../../modules/argocd"

  namespace     = "argocd"
  chart_version = var.argocd_chart_version
}
