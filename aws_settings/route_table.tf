resource "aws_route_table" "route_table" {
  vpc_id = aws_vpc.finbrowser_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.finbrowser_gateway.id
  }

  tags = {
    Name = "route-table-${var.project}"
  }
}

resource "aws_route_table_association" "public_subnets_asso" {
  count          = length(var.cidr_public_subnet)
  subnet_id      = element(aws_subnet.public_subnets[*].id, count.index)
  route_table_id = aws_route_table.second_route_table.id
}