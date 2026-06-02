variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "europe-west1"
}

variable "cluster_name" {
  type    = string
  default = "cloud-agnostic-dev"
}

variable "node_count" {
  type    = number
  default = 2
}

variable "machine_type" {
  type    = string
  default = "e2-standard-4"
}

variable "services" {
  type    = set(string)
  default = ["checkout", "payment", "inventory", "user"]
}

variable "istio_version" {
  type    = string
  default = "1.24.2"
}
