variable "project" {
  type = string
}

variable "region" {
  type = string
}

variable "vpc_id" {
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

variable "cluster_name" {
  type = string
}

variable "target_group_arn" {
  type = string
}

variable "execution_role_arn" {
  type = string
}

variable "policies" {
  type = list(string)
}

variable "lb_sg_id" {
  type = string
}

variable "cluster_arn" {
  type = string
}

variable "repository_url" {
  type = string
}