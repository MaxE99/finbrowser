resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.finbrowser_vpc.id

  tags = {
    Name = "igw-${var.project}"
  }
}