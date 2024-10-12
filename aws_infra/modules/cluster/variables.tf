variable "lb_security_group" {
  type        = string
  description = "The ID of the security group associated with the load balancer. This controls inbound and outbound traffic to the load balancer."
}

variable "project" {
  type        = string
  description = "The name of the project."
}

variable "vpc_id" {
  type        = string
  description = "The ID of the VPC in which the resources will be created."
}