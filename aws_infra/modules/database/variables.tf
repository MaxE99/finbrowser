variable "db_name" {
  type        = string
  description = "The name of the database to create within the database instance."
}

variable "db_password" {
  type        = string
  description = "The password for the database user.."
}

variable "db_username" {
  type        = string
  description = "The username for the database."
}

variable "project" {
  type        = string
  description = "The name of the project."
}

variable "subnet_group_name" {
  type        = string
  description = "The name of the subnet group to associate with the database instance, which determines its network accessibility."
}

variable "vpc_id" {
  type        = string
  description = "The ID of the VPC in which the database instance will be created."
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to all resources."
}