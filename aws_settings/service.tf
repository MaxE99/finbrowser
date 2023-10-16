resource "aws_ecs_service" "main_service" {
  name            = "ecs-service-${var.project}"
  cluster         = aws_ecs_cluster.main_cluster.id
  task_definition = aws_ecs_task_definition.ecs_task_definition.arn
  desired_count   = 1

  network_configuration {
    subnets         = [aws_subnet.public.id]
    security_groups = [aws_security_group.security_group.id]
  }

  force_new_deployment = true



  # load_balancer {
  #   target_group_arn = aws_lb_target_group.ecs_tg.arn
  #   container_name   = "dockergs"
  #   container_port   = 80
  # }

  depends_on = [aws_autoscaling_group.ecs_asg]
}