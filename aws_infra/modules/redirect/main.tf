provider "aws" {
  alias  = "virginia"
  region = "us-east-1"
}

locals {
  fqdn = "www.${var.domain}"
}

resource "aws_acm_certificate" "main" {
  domain_name               = var.domain
  validation_method         = "DNS"
  provider                  = aws.virginia
  subject_alternative_names = ["www.${var.domain}"]
  tags                      = var.tags
}

resource "aws_route53_record" "validation" {
  for_each = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = var.zone_id
  provider        = aws.virginia
}

resource "aws_acm_certificate_validation" "main" {
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for record in aws_route53_record.validation : record.fqdn]
  provider                = aws.virginia
}

resource "aws_cloudfront_origin_access_identity" "main" {
  comment = "redirect"
}

resource "aws_s3_bucket" "www_redirect" {
  bucket        = local.fqdn
  force_destroy = true
  tags          = var.tags
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.www_redirect.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

data "aws_iam_policy_document" "s3_access" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.www_redirect.arn}/*"]

    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.main.iam_arn]
    }
  }

  statement {
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.www_redirect.arn]

    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.main.iam_arn]
    }
  }
}

resource "aws_s3_bucket_policy" "main" {
  bucket = aws_s3_bucket.www_redirect.id
  policy = data.aws_iam_policy_document.s3_access.json
}

resource "aws_s3_bucket_ownership_controls" "main" {
  bucket = aws_s3_bucket.www_redirect.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "main" {
  bucket = aws_s3_bucket.www_redirect.id
  acl    = "public-read"
}

resource "aws_s3_bucket_website_configuration" "main" {
  bucket = aws_s3_bucket.www_redirect.id

  redirect_all_requests_to {
    host_name = var.domain
  }
}

resource "aws_cloudfront_distribution" "main" {
  enabled = true
  aliases = [local.fqdn]

  origin {
    origin_id   = "origin-${local.fqdn}"
    domain_name = aws_s3_bucket_website_configuration.main.website_endpoint

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only" # S3 website endpoints only support HTTP, not HTTPS
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id = "origin-${local.fqdn}"
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]

    forwarded_values {
      query_string = true

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 36000
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn            = aws_acm_certificate.main.arn
    ssl_support_method             = "sni-only"
    cloudfront_default_certificate = false
  }

  price_class = "PriceClass_100"
  tags        = var.tags
}

resource "aws_route53_record" "redirect" {
  name    = local.fqdn
  type    = "A"
  zone_id = var.zone_id

  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}