variable "cluster" {
  type = object({
    id   = string
    arn  = string
    name = string
  })
  description = "The ECS cluster details, including the ID, ARN, and name, used to deploy and manage services."
}

variable "env_variables" {
  type = list(map(string))
  description = "A list of environment variables to pass to the container when the service is run. This allows for configuration without changing the container image."
}

variable "execution_role_arn" {
  type        = string
  description = "The Amazon Resource Name (ARN) of the IAM role that ECS uses to pull images and publish logs for the service."
}

variable "project" {
  type        = string
  description = "The name of the project."
}

variable "region" {
  type        = string
  description = "The AWS region where the resources will be created, which determines resource availability and proximity."
}

variable "repository_url" {
  type        = string
  description = "The URL of the container image repository, from which the service will pull its images."
}

variable "security_groups" {
  type        = list(string)
  description = "A list of security group IDs associated with the service, controlling inbound and outbound traffic."
}

variable "service" {
  type = object({
    name                = string
    command             = list(string)
    schedule_expression = string
  })
  description = "The service configuration details, including the service name, command to run, and optional scheduling expression for periodic tasks."
}

variable "service_subnet_ids" {
  type        = list(string)
  description = "A list of subnet IDs where the ECS service will run, ensuring proper network accessibility."
}

variable "target_group_arn" {
  type        = string
  description = "The Amazon Resource Name (ARN) of the load balancer target group to which the service will register its tasks."
}

variable "task_role_arn" {
  type = string
  default = null
  description = "The ARN of the IAM role that ECS tasks will assume for accessing AWS resources such as S3."
}

variable "vpc_id" {
  type        = string
  description = "The ID of the VPC in which the ECS service will be deployed, necessary for network configuration."
}
