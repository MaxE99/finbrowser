################################
# IAM Role                     #
################################

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "main" {
  name               = "${var.project}-RoleForWebTask"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "main" {
  count      = length(var.policies)
  role       = aws_iam_role.main.name
  policy_arn = var.policies[count.index]
}

data "aws_iam_policy_document" "ssm" {
  statement {
    effect = "Allow"

    actions = [
      "ssmmessages:CreateControlChannel",
      "ssmmessages:CreateDataChannel",
      "ssmmessages:OpenControlChannel",
      "ssmmessages:OpenDataChannel"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "ssm" {
  name   = "${var.project}-AllowSSMAccess"
  policy = data.aws_iam_policy_document.ssm.json
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.main.name
  policy_arn = aws_iam_policy.ssm.arn
}

resource "aws_cloudwatch_log_group" "main" {
  name              = "${var.project}-web-app"
  retention_in_days = 30
}

resource "aws_security_group" "cluster" {
  name        = "${var.project}-sg-ecs"
  description = "Allows all egress and ingress for either a load balancer or services which assume the exported SG to the service holding this SG."
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "cluster" {
  security_group_id            = aws_security_group.cluster.id
  from_port                    = 5000
  to_port                      = 5000
  ip_protocol                  = "tcp"
  referenced_security_group_id = var.lb_sg_id
}

resource "aws_vpc_security_group_egress_rule" "cluster" {
  security_group_id = aws_security_group.cluster.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = -1
}


################################
# ECS Service - WebServer      #
################################

resource "aws_ecs_task_definition" "server" {
  family                   = "${var.project}-django-app"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = aws_iam_role.main.arn
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  container_definitions = jsonencode([
    {
      name      = "${var.project}-django-app"
      image     = var.repository_url
      environment = var.env_variables
      command = ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "researchbrowserproject.wsgi:application"]
      portMappings = [{
          protocol      = "tcp"
          containerPort = 5000
          hostPort      = 5000
      }]
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
    Project = var.project
    Name = "ECS Task Definition"
    Description = "Task definition of the django app for the cluster to spin up"
  }
}

resource "aws_ecs_service" "server" {
  name            = "${var.project}-django-app"
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.server.arn
  launch_type     = "FARGATE"
  desired_count   = 1
  force_new_deployment = true

  network_configuration {
    subnets         = var.service_subnet_ids
    assign_public_ip = true
    security_groups = concat(var.security_groups, [aws_security_group.cluster.id])
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "${var.project}-django-app"
    container_port   = 5000
  }

  tags = {
    Project = var.project
    Name = "ECS service"
    Description = "Service of the Django app"
  }
}

resource "aws_appautoscaling_target" "main" {
  max_capacity = 5
  min_capacity = 1
  resource_id = "service/${var.cluster_name}/${aws_ecs_service.server.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace = "ecs"

  tags = {
    Project = var.project
    Name = "Appautoscaling Target"
    Description = "Autoscaling for the fargate cluster"
  }
}

resource "aws_appautoscaling_policy" "memory" {
  name = "${var.project}-memory"
  policy_type = "TargetTrackingScaling"
  resource_id = aws_appautoscaling_target.main.resource_id
  scalable_dimension = aws_appautoscaling_target.main.scalable_dimension
  service_namespace = aws_appautoscaling_target.main.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = 30
  }
}

resource "aws_appautoscaling_policy" "cpu" {
  name = "${var.project}-cpu"
  policy_type = "TargetTrackingScaling"
  resource_id = aws_appautoscaling_target.main.resource_id
  scalable_dimension = aws_appautoscaling_target.main.scalable_dimension
  service_namespace = aws_appautoscaling_target.main.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 30
  }  
}