variable "cluster" {
  type = object({
    id   = string
    arn  = string
    name = string
  })
}

variable "env_variables" {
  type = list(map(string))
}

variable "execution_role_arn" {
  type = string
}

variable "project" {
  type = string
}

variable "region" {
  type = string
}

variable "repository_url" {
  type = string
}

variable "security_groups" {
  type = list(string)
}

variable "service" {
  type = object({
    name                = string
    command             = list(string)
    schedule_expression = string
  })
}

variable "service_subnet_ids" {
  type = list(string)
}

variable "target_group_arn" {
  type = string
}

variable "vpc_id" {
  type = string
}