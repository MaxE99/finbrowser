variable "aws_acm_certificate" {
  type = string
}

variable "domain" {
  type = string
}

variable "lb_subnet_ids" {
  type = list(string)
}

variable "prod_zone_id" {
  type = string
}

variable "project" {
  type = string
}

variable "vpc_id" {
  type = string
}