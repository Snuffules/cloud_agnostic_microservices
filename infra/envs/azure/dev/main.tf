provider "azurerm" {
  features {}
}

module "aks" {
  source = "../../../modules/aks"

  location            = var.location
  resource_group_name = var.resource_group_name
  cluster_name        = var.cluster_name
  acr_name            = var.acr_name
  services            = var.services
  tags                = var.tags
}

provider "kubernetes" {
  host                   = module.aks.kube_config.host
  client_certificate     = base64decode(module.aks.kube_config.client_certificate)
  client_key             = base64decode(module.aks.kube_config.client_key)
  cluster_ca_certificate = base64decode(module.aks.kube_config.cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host                   = module.aks.kube_config.host
    client_certificate     = base64decode(module.aks.kube_config.client_certificate)
    client_key             = base64decode(module.aks.kube_config.client_key)
    cluster_ca_certificate = base64decode(module.aks.kube_config.cluster_ca_certificate)
  }
}

module "istio" {
  source = "../../../modules/istio"

  istio_version = var.istio_version

  depends_on = [
    module.aks
  ]
}
