resource "aws_s3_bucket" "main" {
  bucket        = "${var.project}-assets"
  force_destroy = true

  tags = {
    Project     = var.project
    Name        = "${var.project} S3 bucket"
    Description = "S3 bucket for storing project assets"
  }
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_cloudfront_origin_access_identity" "main" {
  comment = "${var.project}-origin"
}

resource "aws_s3_bucket_policy" "main" {
  bucket = aws_s3_bucket.main.bucket
  policy = jsonencode({
    Statement = [
      {
        Action   = "s3:GetObject"
        Effect   = "Allow"
        Resource = "${aws_s3_bucket.main.arn}/*"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.main.iam_arn
        }
      },
      {
        Action   = "s3:ListBucket"
        Effect   = "Allow"
        Resource = aws_s3_bucket.main.arn
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.main.iam_arn
        }
      }
    ],
    Version = "2012-10-17"
  })
}

resource "aws_s3_bucket_cors_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  cors_rule {
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = [var.domain]
    allowed_headers = ["Origin"]
    expose_headers  = ["Access-Control-Allow-Origin"]
    max_age_seconds = 3600
  }
}

resource "aws_cloudfront_distribution" "main" {
  enabled = true

  origin {
    origin_id   = "${var.project}-origin"
    domain_name = aws_s3_bucket.main.bucket_regional_domain_name

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.main.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    target_origin_id = "${var.project}-origin"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]

    forwarded_values {
      query_string = true
      headers      = ["Origin"] # Forward the Origin header / required for proper CORS handling

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 86400
    default_ttl            = 31536000
    max_ttl                = 31536000
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 5
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true # use acm_certificate for media if you don't want to use the default cloudfront domain
  }

  price_class = "PriceClass_100"

  tags = {
    Project     = var.project
    Name        = "${var.project} Cloudfront distribution"
    Description = "Cloudfront distribution for distributing project assets"
  }
}