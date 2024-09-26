resource "aws_secretsmanager_secret" "main" {
  name = "${var.project}-secrets"
  recovery_window_in_days = 0

  tags = {
    Project = var.project
    Name = "Secretsmanager"
    Description = "Secrets for the django backend"
  }
}

resource "aws_secretsmanager_secret_version" "main" {
  secret_id = aws_secretsmanager_secret.main.id
  secret_string = jsonencode(var.secrets)
}