output "cluster" {
  value = {
    id   = aws_ecs_cluster.main.id
    arn  = aws_ecs_cluster.main.arn
    name = aws_ecs_cluster.main.name
  }
  description = "Details of the ECS cluster, including the ID, ARN, and name of the cluster."
}

output "security_group" {
  value       = aws_security_group.main.id
  description = "The ID of the security group associated with the ECS cluster."
}

output "execution_role_arn" {
  value       = aws_iam_role.main.arn
  description = "The Amazon Resource Name (ARN) of the IAM role used for executing tasks in the ECS cluster."
}
