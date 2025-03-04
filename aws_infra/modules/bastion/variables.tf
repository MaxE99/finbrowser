variable "project" {
  type        = string
  description = "The name of the project."
}

variable "public_ssh_key" {
  type        = string
  description = "The public SSH key to access the instance."
}

variable "security_groups" {
  type        = list(string)
  description = "List of security group IDs to associate with the instance."
}

variable "subnet_id" {
  type        = string
  description = "The subnet ID where the instance will be launched."
}

variable "vpc_id" {
  type        = string
  description = "The VPC ID where the resources will be created."
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to all resources."
}