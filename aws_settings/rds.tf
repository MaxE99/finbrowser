resource "aws_db_instance" "postgres_db" {
  # General settings
  engine                = "postgres"
  engine_version        = "15.4"
  instance_class        = "db.t4g.micro"
  storage_type          = "gp2"
  allocated_storage     = 1
  max_allocated_storage = 10
  db_name               = var.db_name
  username              = var.db_username
  availability_zone     = var.region
  password              = var.db_password

  # Backup and Maintenance
  backup_retention_period     = 1
  maintenance_window          = "Sun:02:00-Sun:03:00"
  apply_immediately           = false
  skip_final_snapshot         = true
  auto_minor_version_upgrade  = true
  allow_major_version_upgrade = true

  # Accessibility and Security
  publicly_accessible          = false
  performance_insights_enabled = true
  deletion_protection          = true
  vpc_security_group_ids       = [aws_security_group.internal_sg.id]

  tags = {
    Name = "rds-${var.project}"
  }
}