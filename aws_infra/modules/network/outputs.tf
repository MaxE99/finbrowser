output "id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public.*.id
}

output "private_subnet_ids" {
  value = aws_subnet.private.*.id
}

output "private_subnet_group_name" {
  value = aws_db_subnet_group.private.name
}

output "default_security_group_id" {
  value = aws_security_group.main.id
}

output "internet_gw_id" {
  value = aws_internet_gateway.main.id
}