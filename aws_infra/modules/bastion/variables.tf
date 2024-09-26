variable "project" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_ssh_key" {
  type = string
}

variable "security_groups" {
  type = list(string)
}

variable "subnet_id" {
  type = string
}