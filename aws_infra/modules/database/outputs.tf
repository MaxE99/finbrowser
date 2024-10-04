output "address" {
  value = aws_db_instance.main.address
}

output "security_group" {
  value = aws_security_group.outbound.id
}