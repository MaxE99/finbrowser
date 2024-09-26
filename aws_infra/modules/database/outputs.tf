output "security_group_id" {
  value = aws_security_group.outbound.id
}

output "id" {
  value = aws_db_instance.main.id
}

output "arn" {
  value = aws_db_instance.main.arn
}

output "address" {
  value = aws_db_instance.main.address
}