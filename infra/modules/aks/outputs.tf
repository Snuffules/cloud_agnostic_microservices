output "cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "acr_login_server" {
  value = azurerm_container_registry.apps.login_server
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.main.kube_config[0]
  sensitive = true
}

output "workload_identity_client_ids" {
  value = {
    for service, identity in azurerm_user_assigned_identity.workload :
    service => identity.client_id
  }
}
