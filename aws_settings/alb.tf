resource "aws_lb" "main_alb" {
  name               = "ecs-alb-${var.project}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.internal_sg.id]
  subnets            = [aws_subnet.public.id]

  tags = {
    Name = "ecs-alb-${var.project}"
  }
}

resource "aws_lb_listener" "main_alb_listener" {
  load_balancer_arn = aws_lb.main_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main_tg.arn
  }
}

resource "aws_lb_target_group" "main_tg" {
  name        = "ecs-target-group-${var.project}"
  port        = 80
  protocol    = "HTTP"
  target_type = "instance"
  vpc_id      = aws_vpc.main_vpc.id

  health_check {
    path = "/"
  }
}
