output "arn" {
  value = aws_secretsmanager_secret.main.arn
}

output "access_policies" {
  description = "IAM policies for read access to secrets of the monitoring app"
  value = [
    {
      name = "read-access-secrets"
      policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
          {
            Action   = ["secretsmanager:GetSecretValue"]
            Effect   = "Allow"
            Resource = aws_secretsmanager_secret.main.arn
          },
        ]
      })
    }
  ]
}