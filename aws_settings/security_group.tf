resource "aws_security_group" "internal_sg" {
  name   = "internal-sg"
  vpc_id = aws_vpc.main_vpc.id

  tags = {
    Name = "internal-sg-${var.project}"
  }
}

resource "aws_security_group" "alb_sg" {
  name = "alb-sg"
  vpc_id = aws_vpc.main_vpc.id

  tags = {
    Name = "alb-sg-${var.project}"
  }
}

resource "aws_security_group_rule" "alb_ingress" {
  type              = "ingress"
  from_port         = 0
  to_port           = 0
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.alb_sg.id
}

resource "aws_security_group_rule" "alb_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.alb_sg.id
}

resource "aws_security_group_rule" "internal_ingress" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443  
  protocol          = "tcp"
  source_security_group_id = aws_security_group.alb_sg.id
  security_group_id = aws_security_group.internal_sg.id
}

resource "aws_security_group_rule" "internal_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.internal_sg.id
}