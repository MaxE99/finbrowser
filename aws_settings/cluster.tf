resource "aws_ecs_cluster" "main_cluster" {
  name = "ecs-cluster-${var.project}"
}