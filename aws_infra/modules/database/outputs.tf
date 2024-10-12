output "address" {
  value       = aws_db_instance.main.address
  description = "The endpoint address of the database instance, used to connect to the database."
}

output "security_group" {
  value       = aws_security_group.outbound.id
  description = "The ID of the outbound security group associated with the resources, used to control outgoing traffic."
}