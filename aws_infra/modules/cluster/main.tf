###############################################################################
# IAM Role
###############################################################################

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
  name               = "${var.project}-ecs-execution"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json

  tags = {
    Project     = var.project
    Name        = "IAM Execution Role"
    Description = "Execution role for ECS cluster tasks to pull images"
  }
}

resource "aws_iam_role_policy_attachment" "main" {
  role       = aws_iam_role.main.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

###############################################################################
# Security Group
###############################################################################

resource "aws_security_group" "main" {
  name        = "${var.project}-sg-ecs"
  description = "Allows all egress and ingress for either a load balancer or services which assume the exported SG to the service holding this SG."
  vpc_id      = var.vpc_id

  tags = {
    Project     = var.project
    Name        = "ECS Security Group"
    Description = "Security group for ECS cluster and related services"
  }
}

resource "aws_vpc_security_group_ingress_rule" "main" {
  security_group_id            = aws_security_group.main.id
  from_port                    = 5000
  to_port                      = 5000
  ip_protocol                  = "tcp"
  referenced_security_group_id = var.lb_security_group
}

###############################################################################
# Cluster
################################################################################

resource "aws_ecs_cluster" "main" {
  name = "${var.project}-ecs-cluster"

  tags = {
    Project     = var.project
    Name        = "ECS Cluster"
    Description = "Cluster to manage the Django application"
  }
}