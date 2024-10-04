###############################################################################
# Security Group
###############################################################################

resource "aws_security_group" "main" {
  name        = "${var.project}-bastion-host"
  description = "Allow SSH tunnel connection to bastion host"
  vpc_id      = var.vpc_id

  tags = {
    Project     = var.project
    Name        = "Bastion host security group"
    Description = "SSH access to bastion host"
  }
}

resource "aws_vpc_security_group_ingress_rule" "main" {
  security_group_id = aws_security_group.main.id
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

###############################################################################
# Instance
###############################################################################

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-arm64"]
  }

  filter {
    name   = "architecture"
    values = ["arm64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_key_pair" "main" {
  key_name   = "${var.project}-bastion-host"
  public_key = var.public_ssh_key

  tags = {
    Project = var.project
    Name    = "Bastion host key pair"
  }
}

resource "aws_instance" "bastion" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = "t4g.nano"
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = concat(var.security_groups, [aws_security_group.main.id])
  associate_public_ip_address = true
  key_name                    = aws_key_pair.main.id

  tags = {
    Project     = var.project
    Name        = "Bastion host"
    Description = "Bastion host for secure access to RDS database"
  }
}