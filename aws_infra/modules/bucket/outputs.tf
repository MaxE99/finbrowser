output "bucket_url" {
  value = "https://${aws_s3_bucket.main.bucket_regional_domain_name}/"
  description = "The URL of the S3 bucket, formatted for regional access."
}