output "cluster_name" {
  value = module.gke.cluster_name
}

output "artifact_registry_repository" {
  value = module.gke.artifact_registry_repository
}

output "workload_service_accounts" {
  value = module.gke.workload_service_accounts
}
