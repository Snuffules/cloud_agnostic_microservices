variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "acr_name" {
  type = string
}

variable "services" {
  description = "Microservice names used for workload identities."
  type        = set(string)
}

variable "tags" {
  type    = map(string)
  default = {}
}
