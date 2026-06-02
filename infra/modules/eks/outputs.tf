output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "cluster_certificate_authority_data" {
  value     = module.eks.cluster_certificate_authority_data
  sensitive = true
}

output "ecr_repository_urls" {
  value = {
    for service, repo in aws_ecr_repository.service :
    service => repo.repository_url
  }
}

output "workload_role_arns" {
  value = {
    for service, role in aws_iam_role.workload :
    service => role.arn
  }
}
