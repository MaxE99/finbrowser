data "aws_secretsmanager_secret" "db_name_secret" {
  name = "finbrowser_db_name"
}

data "aws_secretsmanager_secret" "db_username_secret" {
  name = "finbrowser_db_username"
}