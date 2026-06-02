output "cluster_name" {
  value = module.eks.cluster_name
}

output "ecr_repository_urls" {
  value = module.eks.ecr_repository_urls
}

output "workload_role_arns" {
  value = module.eks.workload_role_arns
}
