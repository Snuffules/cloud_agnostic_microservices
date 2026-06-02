variable "location" {
  type    = string
  default = "westeurope"
}

variable "resource_group_name" {
  type    = string
  default = "rg-cloud-agnostic-dev"
}

variable "cluster_name" {
  type    = string
  default = "cloud-agnostic-dev"
}

variable "acr_name" {
  description = "Globally unique Azure Container Registry name. Use only letters and numbers."
  type        = string
}

variable "services" {
  type    = set(string)
  default = ["checkout", "payment", "inventory", "user"]
}

variable "istio_version" {
  type    = string
  default = "1.24.2"
}

variable "tags" {
  type = map(string)
  default = {
    project = "cloud-agnostic"
    env     = "dev"
  }
}
