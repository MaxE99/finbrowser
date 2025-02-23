output "service_arn" {
  value = aws_ecs_service.main.id
  description = "The ARN of the ECS service"
}