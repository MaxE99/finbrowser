output "default_security_group" {
  value = aws_security_group.main.id
}

output "private_subnet_group_name" {
  value = aws_db_subnet_group.private.name
}

output "public_subnet_ids" {
  value = aws_subnet.public.*.id
}

output "vpc_id" {
  value = aws_vpc.main.id
}