output "cluster_name" {
  value = module.aks.cluster_name
}

output "resource_group_name" {
  value = module.aks.resource_group_name
}

output "acr_login_server" {
  value = module.aks.acr_login_server
}

output "workload_identity_client_ids" {
  value = module.aks.workload_identity_client_ids
}
