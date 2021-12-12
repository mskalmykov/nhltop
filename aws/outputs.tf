output "cluster_id" {
  description = "EKS cluster ID."
  value       = module.eks.cluster_id
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane."
  value       = module.eks.cluster_endpoint
}

output "ecr_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.nhltop.repository_url
}

output "rds_address" {
  description = "RDS address"
  value       = module.db.db_instance_address
}

output "kube_config" {
  description = "kubectl config for EKS"
  value       = module.eks.kubeconfig
}
