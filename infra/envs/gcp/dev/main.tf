provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_client_config" "default" {}

module "gke" {
  source = "../../../modules/gke"

  project_id   = var.project_id
  region       = var.region
  cluster_name = var.cluster_name
  node_count   = var.node_count
  machine_type = var.machine_type
  services     = var.services
}

provider "kubernetes" {
  host  = module.gke.host
  token = data.google_client_config.default.access_token

  cluster_ca_certificate = base64decode(module.gke.cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host  = module.gke.host
    token = data.google_client_config.default.access_token

    cluster_ca_certificate = base64decode(module.gke.cluster_ca_certificate)
  }
}

module "istio" {
  source = "../../../modules/istio"

  istio_version = var.istio_version

  depends_on = [
    module.gke
  ]
}
