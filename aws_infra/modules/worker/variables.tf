variable "project" {
  type = string
}

variable "region" {
  type = string
}

variable "service_subnet_ids" {
  type = list(string)
}

variable "security_groups" {
  type = list(string)
}

variable "env_variables" {
  type = list(map(string))
}

variable "cluster_id" {
  type = string
}

variable "execution_role_arn" {
  type = string
}

variable "cluster_arn" {
  type = string
}

variable "repository_url" {
  type = string
}

variable "worker" {
  type = string
}

variable "task_role_arn" {
  type = string
}

variable "command" {
  type = list(string)
}

variable "schedule_expression" {
  type = string
}