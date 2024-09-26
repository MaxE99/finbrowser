variable "project" {
  type    = string
  default = "finbrowser"
}

variable "region" {
  type    = string
  default = "us-east-2"
}

variable "db_name" {
  type      = string
  sensitive = true
}

variable "db_username" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "domain" {
  type    = string
  default = "ebert-test-domain.com"
}

variable "public_ssh_key_file_path" {
  type    = string
  default = ""
}

variable "prod_zone_id" {
  type    = string
  default = "Z03766462O143CYRIVTVM"
}

variable "database_hostname" {
  type      = string
  sensitive = true
}

variable "django_settings_module" {
  type      = string
  sensitive = true
}

variable "email_host_user" {
  type      = string
  sensitive = true
}

variable "email_host_password" {
  type      = string
  sensitive = true
}

variable "secret_key" {
  type      = string
  sensitive = true
}