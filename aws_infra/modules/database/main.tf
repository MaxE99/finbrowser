###############################################################################
# Security Group
################################################################################

resource "aws_security_group" "outbound" {
  name        = "${var.project}-rds-egress"
  description = "Allows services with this security group to access the RDS instance"
  vpc_id      = var.vpc_id
  tags        = var.tags
}

resource "aws_security_group" "inbound" {
  name        = "${var.project}-rds-ingress"
  description = "Allows RDS instance to be accessed by services"
  vpc_id      = var.vpc_id
  tags        = var.tags
}

resource "aws_vpc_security_group_egress_rule" "outbound" {
  security_group_id            = aws_security_group.outbound.id
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.inbound.id
}

resource "aws_vpc_security_group_ingress_rule" "inbound" {
  security_group_id            = aws_security_group.inbound.id
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.outbound.id
}

###############################################################################
# RDS
################################################################################

resource "aws_db_instance" "main" {
  identifier                  = "${var.project}-rds"
  allocated_storage           = 20
  max_allocated_storage       = 25
  db_name                     = var.db_name
  engine                      = "postgres"
  engine_version              = "15.5"
  auto_minor_version_upgrade  = false
  allow_major_version_upgrade = true
  instance_class              = "db.t4g.micro"
  username                    = var.db_username
  password                    = var.db_password
  port                        = "5432"
  skip_final_snapshot         = false
  db_subnet_group_name        = var.subnet_group_name
  vpc_security_group_ids      = [aws_security_group.inbound.id]
  deletion_protection         = true
  tags                        = var.tags
}