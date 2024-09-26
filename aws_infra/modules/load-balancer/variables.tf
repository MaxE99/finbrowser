variable "project" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "lb_subnet_ids" {
  type = list(string)
}

variable "aws_acm_certificate" {
  type = string
}

