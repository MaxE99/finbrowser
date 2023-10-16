resource "aws_ecs_capacity_provider" "main_capacity_provider" {
  name = "capacity-provider-${var.project}"

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.ecs_asg.arn

    managed_scaling {
      maximum_scaling_step_size = 3
      minimum_scaling_step_size = 1
      status                    = "ENABLED"
      target_capacity           = 1
    }
  }
}

resource "aws_ecs_cluster_capacity_providers" "main_cluster_capacity_provider" {
  cluster_name = aws_ecs_cluster.main_cluster.name

  capacity_providers = [aws_ecs_capacity_provider.main_capacity_provider.name]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = aws_ecs_capacity_provider.main_capacity_provider.name
  }
}