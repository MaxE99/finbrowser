################################
# Security Groups              #
################################

resource "aws_security_group" "main" {
  name        = "${var.project}-egress-cluster"
  description = "Allows services with this security group to access the tasks in the cluster"
  vpc_id      = var.vpc_id

  tags = {
    Project = var.project
    Name = "Load balancer security group"
    Description = "Allows services with this security group to access the tasks in the cluster"
  }
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.main.id
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "https" {
  security_group_id = aws_security_group.main.id
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "main" {
  security_group_id = aws_security_group.main.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = -1
}

################################
# Load Balancer                #
################################

data "aws_elb_service_account" "main" {}

resource "aws_s3_bucket" "elb_logs" {
  bucket = "my-elb-tf-test-bucket-13082032"
  force_destroy = true
}

resource "aws_s3_bucket_ownership_controls" "example" {
  bucket = aws_s3_bucket.elb_logs.id
  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_acl" "example" {
  depends_on = [aws_s3_bucket_ownership_controls.example]

  bucket = aws_s3_bucket.elb_logs.id
  acl    = "private"
}

data "aws_iam_policy_document" "allow_elb_logging" {
  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = [data.aws_elb_service_account.main.arn]
    }

    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.elb_logs.arn}/AWSLogs/*"]
  }
}

resource "aws_s3_bucket_policy" "allow_elb_logging" {
  bucket = aws_s3_bucket.elb_logs.id
  policy = data.aws_iam_policy_document.allow_elb_logging.json
}

resource "aws_lb" "main" {
  name               = "${var.project}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.main.id]
  subnets            = var.lb_subnet_ids
  idle_timeout = 600

  enable_deletion_protection = false
  enable_cross_zone_load_balancing = true

  access_logs {
    bucket  = aws_s3_bucket.elb_logs.id
    enabled = true
  }

  tags = {
    Project = var.project
    Name = "Application load balancer"
    Description = "Application load balancer for the django app service"
  }
}

################################
# Target Group                 #
################################

resource "aws_lb_target_group" "main" {
  name        = "${var.project}-lb-target-group"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    healthy_threshold   = 3
    interval            = 30
    protocol            = "HTTP"
    matcher             = "200"
    timeout             = 10
    path                = "/" # endpoint of the django app for health check
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.id
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "redirect"

    redirect {
      port = 443
      protocol = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.id
  port              = 443
  protocol          = "HTTPS"

  ssl_policy = "ELBSecurityPolicy-2016-08"
  certificate_arn = var.aws_acm_certificate

  default_action {
    target_group_arn = aws_lb_target_group.main.id
    type = "forward"
  }
}

resource "aws_lb_listener_certificate" "https" {
  listener_arn    = aws_lb_listener.https.arn
  certificate_arn = var.aws_acm_certificate
}
