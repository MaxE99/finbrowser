module "network" {
  source = "./modules/network"

  project = var.project
}

module "database" {
  source = "./modules/database"

  project           = var.project
  vpc_id            = module.network.id
  subnet_group_name = module.network.private_subnet_group_name
  db_name           = var.db_name
  db_username       = var.db_username
  db_password       = var.db_password
}

module "bucket" {
  source = "./modules/bucket"

  project = var.project
}

module "secrets" {
  source = "./modules/secrets"

  project = var.project
  secrets = {
    DB_NAME            = var.db_name
    DB_USER            = var.db_username
    DB_MASTER_PASSWORD = var.db_password
    DB_HOSTNAME        = var.database_hostname
    EMAIL_USER         = var.email_host_user
    EMAIL_PW           = var.email_host_password
    SECRET_KEY         = var.secret_key
    S3_BUCKET          = module.bucket.bucket_url
  }
}

module "bastion_host" {
  source = "./modules/bastion"

  project   = var.project
  vpc_id    = module.network.id
  subnet_id = module.network.public_subnet_ids[0]
  security_groups = [
    module.network.default_security_group_id,
    module.database.security_group_id
  ]
  public_ssh_key = file(var.public_ssh_key_file_path)
}

module "certificate" {
  source = "./modules/certificate"

  domain  = var.domain
  zone_id = var.prod_zone_id
}

module "load_balancer" {
  source = "./modules/load-balancer"

  project             = var.project
  vpc_id              = module.network.id
  lb_subnet_ids       = module.network.public_subnet_ids
  aws_acm_certificate = module.certificate.arn
}

resource "aws_route53_record" "lb" {
  zone_id = var.prod_zone_id
  name    = var.domain
  type    = "A"

  alias {
    name                   = module.load_balancer.dns_name
    zone_id                = module.load_balancer.zone_id
    evaluate_target_health = true
  }
}

module "cluster" {
  source = "./modules/cluster"

  project = var.project
}

resource "aws_ecr_repository" "main" {
  name = "${var.project}-django-app"
  image_tag_mutability = "MUTABLE"
  force_delete = true

  tags = {
    Project = var.project
    Name = "ECR Repository"
    Description = "Image of the Django app for the cluster to spin up and execute"
  }
}

module "service" {
  source = "./modules/service"

  project            = var.project
  region             = var.region
  vpc_id             = module.network.id
  service_subnet_ids = module.network.public_subnet_ids
  cluster_id         = module.cluster.cluster_id
  cluster_arn        = module.cluster.cluster_arn 
  cluster_name       = module.cluster.cluster_name
  target_group_arn   = module.load_balancer.target_group_arn
  execution_role_arn = module.cluster.execution_role_arn
  policies           = [module.secrets.arn]
  lb_sg_id           = module.load_balancer.lb_sg_id 
  env_variables = [
    {
      name  = "DB_NAME"
      value = var.db_name
    },
    {
      name  = "DB_USER"
      value = var.db_username
    },
    {
      name  = "DB_MASTER_PASSWORD"
      value = var.db_password
    },
    {
      name  = "DB_HOSTNAME"
      value = var.database_hostname
    },
    {
      name  = "EMAIL_USER"
      value = var.email_host_user
    },
    {
      name  = "EMAIL_PW"
      value = var.email_host_password
    },
    {
      name  = "SECRET_KEY"
      value = var.secret_key
    },
    {
      name  = "S3_BUCKET"
      value = module.bucket.bucket_url
    }
  ]
  security_groups = [
    module.network.default_security_group_id,
    module.database.security_group_id
  ]
  repository_url = aws_ecr_repository.main.repository_url
}

data "aws_iam_policy_document" "worker_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "worker" {
  name               = "${var.project}-RoleForWorkerTasks"
  assume_role_policy = data.aws_iam_policy_document.worker_assume_role.json
}

resource "aws_iam_role_policy_attachment" "worker" {
  count      = length([module.secrets.arn])
  role       = aws_iam_role.worker.name
  policy_arn = [module.secrets.arn][count.index]
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
  name   = "${var.project}-workers-AllowSSMAccess"
  policy = data.aws_iam_policy_document.ssm.json
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.worker.name
  policy_arn = aws_iam_policy.ssm.arn
}

resource "aws_security_group" "worker" {
  name        = "${var.project}-worker-sg-ecs"
  description = "Allows all egress and ingress for either a load balancer or services which assume the exported SG to the service holding this SG."
  vpc_id      = module.network.id
}

resource "aws_vpc_security_group_egress_rule" "worker" {
  security_group_id = aws_security_group.worker.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = -1
}

variable "workers" {
  type = list(object({
    name               = string
    command            = list(string)
    schedule_expression = string
  }))
  default = [
    {
      name               = "youtube"
      command            = ["python", "manage.py", "scrape_youtube"]
      schedule_expression = "rate(5 minutes)"
    },
    {
      name               = "spotify"
      command            = ["python", "manage.py", "scrape_spotify"]
      schedule_expression = "rate(5 minutes)"
    },
    # {
    #   name               = "forbes"
    #   command            = ["python", "manage.py", "scrape_forbes"]
    #   schedule_expression = "rate(24 hours)"
    # },
    # {
    #   name               = "calc-sim"
    #   command            = ["python", "manage.py", "calculate_similiar_sources"]
    #   schedule_expression = "rate(28 days)"
    # },
    # {
    #   name               = "expired-notifications"
    #   command            = ["python", "manage.py", "delete_expired_notifications"]
    #   schedule_expression = "rate(24 hours)"
    # },
    # {
    #   name               = "innacurate_youtube_articles"
    #   command            = ["python", "manage.py", "delete_innacurate_youtube_articles"]
    #   schedule_expression = "rate(28 days)"
    # },
    # {
    #   name               = "other_websites"
    #   command            = ["python", "manage.py", "scrape_other_websites"]
    #   schedule_expression = "rate(24 hours)"
    # },
    # {
    #   name               = "problematic_feeds"
    #   command            = ["python", "manage.py", "scrape_problematic_feeds"]
    #   schedule_expression = "rate(24 hours)"
    # },
    # {
    #   name               = "seeking_alpha"
    #   command            = ["python", "manage.py", "scrape_seeking_alpha"]
    #   schedule_expression = "rate(24 hours)"
    # },
    # {
    #   name               = "substack"
    #   command            = ["python", "manage.py", "scrape_substack"]
    #   schedule_expression = "rate(24 hours)"
    # },
    # {
    #   name               = "spotify_profile_imgs"
    #   command            = ["python", "manage.py", "update_spotify_profile_imgs"]
    #   schedule_expression = "rate(28 days)"
    # },
    # {
    #   name               = "youtube_profile_imgs"
    #   command            = ["python", "manage.py", "update_youtube_profile_imgs"]
    #   schedule_expression = "rate(28 days)"
    # }
  ]
}

module "workers" {
  for_each = { for worker in var.workers : worker.name => worker }

  source = "./modules/worker"

  project            = var.project
  region             = var.region
  service_subnet_ids = module.network.public_subnet_ids
  cluster_id         = module.cluster.cluster_id
  cluster_arn        = module.cluster.cluster_arn 
  execution_role_arn = module.cluster.execution_role_arn
  env_variables = [
    {
      name  = "DB_NAME"
      value = var.db_name
    },
    {
      name  = "DB_USER"
      value = var.db_username
    },
    {
      name  = "DB_MASTER_PASSWORD"
      value = var.db_password
    },
    {
      name  = "DB_HOSTNAME"
      value = var.database_hostname
    },
    {
      name  = "EMAIL_USER"
      value = var.email_host_user
    },
    {
      name  = "EMAIL_PW"
      value = var.email_host_password
    },
    {
      name  = "SECRET_KEY"
      value = var.secret_key
    },
    {
      name  = "S3_BUCKET"
      value = module.bucket.bucket_url
    }
  ]
  security_groups = [
    module.network.default_security_group_id,
    module.database.security_group_id,
    aws_security_group.worker.id
  ]
  repository_url      = aws_ecr_repository.main.repository_url
  worker              = each.key
  task_role_arn       = aws_iam_role.worker.arn
  command             = each.value.command
  schedule_expression = each.value.schedule_expression
}