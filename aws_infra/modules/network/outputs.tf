output "default_security_group" {
  value       = aws_security_group.main.id
  description = "The ID of the default security group created for the VPC. This security group controls inbound and outbound traffic for resources within the VPC."
}

output "private_subnet_group_name" {
  value       = aws_db_subnet_group.private.name
  description = "The name of the subnet group that contains private subnets for database resources, ensuring secure access."
}

output "public_subnet_ids" {
  value       = aws_subnet.public.*.id
  description = "A list of IDs for the public subnets within the VPC, where resources can be exposed to the internet."
}

output "vpc_id" {
  value       = aws_vpc.main.id
  description = "The ID of the VPC created for the network infrastructure, serving as a container for all networking resources."
}
