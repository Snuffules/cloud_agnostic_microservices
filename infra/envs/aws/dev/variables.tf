variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "cluster_name" {
  type    = string
  default = "cloud-agnostic-dev"
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
