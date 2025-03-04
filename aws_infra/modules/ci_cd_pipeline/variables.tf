variable "bucket_arn" {
  type        = string
  description = "The ARN of the S3 bucket used for storing media assets"
}

variable "cloudfront_arn" {
  type        = string
  description = "The ARN of the CloudFront distribution to invalidate the cache"
}

variable "ecr_repository_arn" {
  type        = string
  description = "The ARN of the Amazon ECR repository used for storing Docker images"
}

variable "github_repository" {
  type        = string
  description = "The GitHub repository in the format 'org/repo' that will assume this IAM role"
}

variable "project" {
  type        = string
  description = "The project name used for naming AWS resources"
}

variable "service_arn" {
  type        = string
  description = "The ARN of the ECS service that GitHub Actions will update"
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to all resources."
}