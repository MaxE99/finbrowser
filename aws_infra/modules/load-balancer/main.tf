################################################################################
# Security Group
################################################################################

resource "aws_security_group" "main" {
  name        = "${var.project}-cluster-access"
  description = "Allows services with this security group to access the tasks in the cluster"
  vpc_id      = var.vpc_id

  tags = {
    Project     = var.project
    Name        = "Load balancer security group"
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

################################################################################
# Target Group
################################################################################

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
    path                = "/health-check" # endpoint of the django app for health check
    unhealthy_threshold = 2
  }

  tags = {
    Project     = var.project
    Name        = "LB Target Group"
    Description = "Target group for the web app load balancer"
  }
}

################################################################################
# Load Balancer
################################################################################

resource "aws_lb" "main" {
  name                             = "${var.project}-alb"
  internal                         = false
  load_balancer_type               = "application"
  security_groups                  = [aws_security_group.main.id]
  subnets                          = var.lb_subnet_ids
  idle_timeout                     = 600

  tags = {
    Project     = var.project
    Name        = "Application load balancer"
    Description = "Application load balancer for the web app"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.id
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = 443
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.id
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.aws_acm_certificate

  default_action {
    target_group_arn = aws_lb_target_group.main.id
    type             = "forward"
  }
}

resource "aws_lb_listener_certificate" "https" {
  listener_arn    = aws_lb_listener.https.arn
  certificate_arn = var.aws_acm_certificate
}

################################################################################
# Route53
################################################################################

resource "aws_route53_record" "lb" {
  zone_id = var.prod_zone_id
  name    = var.domain
  type    = "A"

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}