output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "cluster_id" {
  value = aws_ecs_cluster.main.id
}

output "cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

output "execution_role_arn" {
  value = aws_iam_role.main.arn
}