resource "aws_ecs_cluster" "main" {
  name = "${var.project}-main-ecs-cluster"

  tags = {
    Project = var.project
    Name = "ECS Cluster"
    Description = "Cluster to manage the Django application"
  }
}

data "aws_iam_policy_document" "assume_role"{
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "main" {
  name = "${var.project}-ecs-execution"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json

  tags = {
    Project = var.project
    Name = "IAM Execution Role"
    Description = "Execution role for ECS cluster tasks to pull images"
  }
}

resource "aws_iam_role_policy_attachment" "service" {
  role = aws_iam_role.main.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
