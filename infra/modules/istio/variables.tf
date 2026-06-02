variable "istio_version" {
  description = "Istio Helm chart version."
  type        = string
  default     = "1.24.2"
}

variable "gateway_service_annotations" {
  description = "Annotations added to the Istio ingress gateway service."
  type        = map(string)
  default     = {}
}
