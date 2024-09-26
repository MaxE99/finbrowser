resource "aws_cloudwatch_log_group" "main" {
  name              = "${var.project}-${var.worker}-worker"
  retention_in_days = 30
}

resource "aws_ecs_task_definition" "main" {
  family                   = "${var.project}-${var.worker}-worker"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  container_definitions = jsonencode([
    {
      name      = "${var.project}-${var.worker}-worker"
      image     = var.repository_url
      environment = var.env_variables
      command = var.command
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
    Worker = var.worker
    Name = "ECS Workers Task Definition"
  }
}

resource "aws_ecs_service" "main" {
  name            = "${var.project}-${var.worker}-worker"
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.main.arn
  launch_type     = "FARGATE"
  desired_count   = 0
  force_new_deployment = true

  network_configuration {
    subnets         = var.service_subnet_ids
    assign_public_ip = true
    security_groups = var.security_groups
  }

  tags = {
    Project = var.project
    Worker = var.worker
    Name = "ECS Workers service"
  }
}

resource "aws_iam_role" "main" {
  name = "${var.project}-${var.worker}-ecs-eventbridge-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = {
        Service = "events.amazonaws.com"
      },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "main" {
  role       = aws_iam_role.main.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
}

resource "aws_iam_role_policy" "main" {
  name   = "${var.project}-${var.worker}-ecs-eventbridge-policy"
  role   = aws_iam_role.main.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ecs:RunTask",
          "ecs:StopTask",
          "iam:PassRole"
        ],
        Resource = [
          aws_ecs_task_definition.main.arn,
          var.execution_role_arn
        ]
      }
    ]
  })
}

resource "aws_cloudwatch_event_rule" "main" {
  name                = "${var.project}-${var.worker}-worker"
  schedule_expression = var.schedule_expression
}

resource "aws_cloudwatch_event_target" "main" {
  rule      = aws_cloudwatch_event_rule.main.name
  arn       = var.cluster_arn
  role_arn  = aws_iam_role.main.arn

  ecs_target {
    launch_type          = "FARGATE"
    task_definition_arn  = aws_ecs_task_definition.main.arn
    network_configuration {
      subnets         = var.service_subnet_ids
      assign_public_ip = true
      security_groups = var.security_groups
    }
    platform_version = "LATEST"
  }
}