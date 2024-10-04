output "cluster" {
  value = {
    id   = aws_ecs_cluster.main.id
    arn  = aws_ecs_cluster.main.arn
    name = aws_ecs_cluster.main.name
  }
}

output "security_group" {
  value = aws_security_group.main.id
}

output "execution_role_arn" {
  value = aws_iam_role.main.arn
}