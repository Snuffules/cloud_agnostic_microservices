variable "namespace" {
  description = "Namespace where Argo CD will be installed."
  type        = string
  default     = "argocd"
}

variable "chart_version" {
  description = "Optional argo-cd Helm chart version. Leave null to use the latest chart available at install time."
  type        = string
  default     = null
}
