output "cluster_name" {
  value = google_container_cluster.main.name
}

output "host" {
  value = "https://${google_container_cluster.main.endpoint}"
}

output "cluster_ca_certificate" {
  value     = google_container_cluster.main.master_auth[0].cluster_ca_certificate
  sensitive = true
}

output "artifact_registry_repository" {
  value = google_artifact_registry_repository.apps.name
}

output "workload_service_accounts" {
  value = {
    for service, account in google_service_account.workload :
    service => account.email
  }
}
