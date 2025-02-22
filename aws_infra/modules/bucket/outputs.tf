output "bucket_arn" {
  value = aws_s3_bucket.main.arn
  description = "The ARN of the S3 bucket used for storing FinBrowser assets."
}

output "bucket_name" {
  value       = aws_s3_bucket.main.id
  description = "The name of the S3 bucket used for storing FinBrowser assets."
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.main.domain_name
  description = "The CloudFront distribution domain for accessing media assets securely."
}