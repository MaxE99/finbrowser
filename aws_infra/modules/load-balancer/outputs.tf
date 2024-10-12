output "security_group" {
  value       = aws_security_group.main.id
  description = "The ID of the main security group associated with the load balancer. This controls inbound and outbound traffic."
}

output "target_group_arn" {
  value       = aws_lb_target_group.main.arn
  description = "The Amazon Resource Name (ARN) of the load balancer target group, used for routing requests to the appropriate targets."
}
