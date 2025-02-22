variable "domain" {
  type = string
  description = "The domain that is allowed to make cross-origin requests to the CloudFront distribution, which serves the S3 bucket resources."
}

variable "project" {
  type = string
  description = "The name of the project."
}