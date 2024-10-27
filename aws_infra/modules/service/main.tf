################################################################################
# Cloudwatch Log Group
################################################################################

resource "aws_cloudwatch_log_group" "main" {
  name              = "${var.project}-${var.service.name}"
  retention_in_days = 30

  tags = {
    Project     = var.project
    Name        = "CloudWatch Log Group"
    Description = "Log group for ECS service logs"
  }
}

################################################################################
# ECS
################################################################################

resource "aws_ecs_task_definition" "main" {
  family                   = "${var.project}-${var.service.name}"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = var.execution_role_arn
  network_mode             = "awsvpc"
  cpu                      = var.service.schedule_expression == null ? 512 : 256
  memory                   = var.service.schedule_expression == null ? 1024 : 512
  container_definitions = jsonencode([
    {
      name        = "${var.project}-${var.service.name}"
      image       = var.repository_url
      environment = var.env_variables
      command     = var.service.command
      portMappings = var.service.schedule_expression == null ? [{
        protocol      = "tcp"
        containerPort = 5000
        hostPort      = 5000
      }] : []
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.main.id
          awslogs-region        = var.region
          awslogs-stream-prefix = "service"
        }
      }
    }
  ])

  tags = {
    Project     = var.project
    Name        = "${var.project} ${var.service.name} ecs task definition"
    Description = "Task definition of the django app for the cluster to spin up"
  }
}

resource "aws_ecs_service" "main" {
  name                 = "${var.project}-${var.service.name}"
  cluster              = var.cluster.id
  task_definition      = aws_ecs_task_definition.main.arn
  launch_type          = "FARGATE"
  desired_count        = var.service.schedule_expression == null ? 1 : 0
  force_new_deployment = true

  network_configuration {
    subnets          = var.service_subnet_ids
    assign_public_ip = true
    security_groups  = var.security_groups
  }

  dynamic "load_balancer" {
    for_each = var.service.schedule_expression == null ? [1] : []
    content {
      target_group_arn = var.target_group_arn
      container_name   = "${var.project}-${var.service.name}"
      container_port   = 5000
    }
  }

  tags = {
    Project     = var.project
    Name        = "${var.project} ${var.service.name} ecs service"
    Description = "Service of the Django app"
  }
}

################################################################################
# Web Server - Autoscaling
################################################################################

resource "aws_appautoscaling_target" "main" {
  count              = var.service.schedule_expression == null ? 1 : 0
  max_capacity       = 5
  min_capacity       = 1
  resource_id        = "service/${var.cluster.name}/${aws_ecs_service.main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  tags = {
    Project     = var.project
    Name        = "Appautoscaling Target"
    Description = "Autoscaling for the fargate cluster"
  }
}

resource "aws_appautoscaling_policy" "memory" {
  count              = var.service.schedule_expression == null ? 1 : 0
  name               = "${var.project}-memory"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.main[0].resource_id
  scalable_dimension = aws_appautoscaling_target.main[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.main[0].service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = 60
  }
}

resource "aws_appautoscaling_policy" "cpu" {
  count              = var.service.schedule_expression == null ? 1 : 0
  name               = "${var.project}-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.main[0].resource_id
  scalable_dimension = aws_appautoscaling_target.main[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.main[0].service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 60
  }
}

################################################################################
# Workers - IAM Role
################################################################################

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "main" {
  count              = var.service.schedule_expression != null ? 1 : 0
  name               = "${var.project}-${var.service.name}-ecs-eventbridge-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json

  tags = {
    Project     = var.project
    Name        = "${var.project} ${var.service.name} IAM Role for EventBridge"
    Description = "Role for ECS tasks triggered by EventBridge"
  }
}

resource "aws_iam_role_policy_attachment" "main" {
  count      = var.service.schedule_expression != null ? 1 : 0
  role       = aws_iam_role.main[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
}

data "aws_iam_policy_document" "ecs_eventbridge_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ecs:RunTask",
      "ecs:StopTask",
      "iam:PassRole"
    ]
    resources = [
      aws_ecs_task_definition.main.arn,
      var.execution_role_arn
    ]
  }
}

resource "aws_iam_role_policy" "main" {
  count  = var.service.schedule_expression != null ? 1 : 0
  name   = "${var.project}-${var.service.name}-ecs-eventbridge-policy"
  role   = aws_iam_role.main[0].id
  policy = data.aws_iam_policy_document.ecs_eventbridge_policy.json
}

################################################################################
# Workers - Cloudwatch Event Target
################################################################################

resource "aws_cloudwatch_event_rule" "main" {
  count               = var.service.schedule_expression != null ? 1 : 0
  name                = "${var.project}-${var.service.name}-worker"
  schedule_expression = var.service.schedule_expression

  tags = {
    Project     = var.project
    Name        = "${var.project} ${var.service.name} CloudWatch Event Rule"
    Description = "CloudWatch event rule for scheduling ECS tasks"
  }
}

resource "aws_cloudwatch_event_target" "main" {
  count    = var.service.schedule_expression != null ? 1 : 0
  rule     = aws_cloudwatch_event_rule.main[0].name
  arn      = var.cluster.arn
  role_arn = aws_iam_role.main[0].arn

  ecs_target {
    launch_type         = "FARGATE"
    task_definition_arn = aws_ecs_task_definition.main.arn
    network_configuration {
      subnets          = var.service_subnet_ids
      assign_public_ip = true
      security_groups  = var.security_groups
    }
    platform_version = "LATEST"
  }
}