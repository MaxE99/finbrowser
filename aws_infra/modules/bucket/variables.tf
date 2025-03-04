variable "domain" {
  type        = string
  description = "The domain that is allowed to make cross-origin requests to the CloudFront distribution, which serves the S3 bucket resources."
}

variable "project" {
  type        = string
  description = "The name of the project."
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to all resources."
}