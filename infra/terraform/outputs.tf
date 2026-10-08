output "api_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "enterprise_tools_repository_url" {
  value = aws_ecr_repository.tools.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.this.name
}
