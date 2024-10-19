output "acm_arn" {
  value       = aws_acm_certificate.main.arn
  description = "The Amazon Resource Name (ARN) of the ACM certificate, which can be used to reference the certificate in other AWS services."
}