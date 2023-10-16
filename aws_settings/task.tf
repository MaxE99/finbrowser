resource "aws_ecs_task_definition" "ecs_task_definition" {
  family             = "ecs-task-${var.project}"
  network_mode       = "awsvpc"
  execution_role_arn = "arn:aws:iam::532199187081:role/ecsTaskExecutionRole"
  cpu                = 256
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
  container_definitions = jsonencode([
    {
      name      = "django-app"
      image     = "your-django-app-image:latest"
      memory    = 512
      cpu       = 256
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      environment = [
        {
          name  = "DJANGO_SETTINGS_MODULE",
          value = "yourapp.settings"
        },
        {
          name  = "SECRET_KEY",
          value = "your-secret-key"
        },
        {
          name  = "DEBUG",
          value = "false"
        }
        # Add more environment variables as needed
      ]
    }
  ])
}