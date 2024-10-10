output "bucket_url" {
  value = "https://${aws_s3_bucket.main.bucket_regional_domain_name}/"
}