output "security_group" {
  value = aws_security_group.main.id
}

output "target_group_arn" {
  value = aws_lb_target_group.main.arn
}