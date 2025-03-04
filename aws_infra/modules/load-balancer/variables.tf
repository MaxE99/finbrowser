variable "aws_acm_certificate" {
  type        = string
  description = "The ARN of the AWS ACM certificate to use for SSL termination with the load balancer."
}

variable "domain" {
  type        = string
  description = "The domain name associated with the project, used for DNS configuration and SSL certificate validation."
}

variable "lb_subnet_ids" {
  type        = list(string)
  description = "A list of subnet IDs where the load balancer will be deployed. These subnets should be in the same VPC."
}

variable "prod_zone_id" {
  type        = string
  description = "The ID of the Route 53 hosted zone for the production environment, used for DNS record management."
}

variable "project" {
  type        = string
  description = "The name of the project."
}

variable "vpc_id" {
  type        = string
  description = "The ID of the VPC in which the resources will be created."
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to all resources."
}