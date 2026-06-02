variable "region" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "services" {
  description = "Microservice names used for ECR and IRSA roles."
  type        = set(string)
}

variable "tags" {
  type    = map(string)
  default = {}
}
