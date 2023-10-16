resource "aws_subnet" "public" {
  count             = length(var.cidr_public_subnet)
  vpc_id            = aws_vpc.finbrowser_vpc.id
  cidr_block        = element(var.cidr_public_subnet, count.index)
  availability_zone = element(var.availability_zones, count.index)

  tags = {
    Name = "public-subnet-${count.index + 1}-${var.project}"
  }
}

resource "aws_subnet" "private" {
  count             = length(var.cidr_private_subnet)
  vpc_id            = aws_vpc.finbrowser_vpc.id
  cidr_block        = element(var.cidr_private_subnet, count.index)
  availability_zone = element(var.availability_zones, count.index)

  tags = {
    Name = "private-subnet-${count.index + 1}-${var.project}"
  }
}