locals {
  domain       = "finbrowser.io"
  prod_zone_id = "Z0063739EBD6ODRQ14EA"
  project      = "finbrowser"
  region       = "us-east-2"
  workers = [
    {
      name                = "youtube"
      command             = ["python", "manage.py", "scrape_youtube"]
      schedule_expression = "rate(24 hours)"
    },
    {
      name                = "spotify"
      command             = ["python", "manage.py", "scrape_spotify"]
      schedule_expression = "rate(24 hours)"
    },
    {
      name                = "calc-sim"
      command             = ["python", "manage.py", "calculate_similiar_sources"]
      schedule_expression = "rate(28 days)"
    },
    {
      name                = "expired-notifications"
      command             = ["python", "manage.py", "delete_expired_notifications"]
      schedule_expression = "rate(24 hours)"
    },
    {
      name                = "innacurate_youtube_articles"
      command             = ["python", "manage.py", "delete_innacurate_youtube_articles"]
      schedule_expression = "rate(28 days)"
    },
    {
      name                = "other_websites"
      command             = ["python", "manage.py", "scrape_other_websites"]
      schedule_expression = "rate(24 hours)"
    },
    {
      name                = "problematic_feeds"
      command             = ["python", "manage.py", "scrape_problematic_feeds"]
      schedule_expression = "rate(24 hours)"
    },
    {
      name                = "seeking_alpha"
      command             = ["python", "manage.py", "scrape_seeking_alpha"]
      schedule_expression = "rate(24 hours)"
    },
    {
      name                = "substack"
      command             = ["python", "manage.py", "scrape_substack"]
      schedule_expression = "rate(24 hours)"
    },
    {
      name                = "spotify_profile_imgs"
      command             = ["python", "manage.py", "update_spotify_profile_imgs"]
      schedule_expression = "rate(28 days)"
    },
    {
      name                = "youtube_profile_imgs"
      command             = ["python", "manage.py", "update_youtube_profile_imgs"]
      schedule_expression = "rate(28 days)"
    }
  ]

  common_tags = {
    Author      = "Max Ebert"
    Environment = "Production"
    ManagedBy   = "Terraform"
    Repository  = "https://github.com/MaxE99/finbrowser/"
    Project     = "finbrowser"
  }
}

module "bucket" {
  source = "./modules/bucket"

  domain  = "https://${local.domain}"
  project = local.project
  tags    = local.common_tags
}

module "network" {
  source = "./modules/network"

  project = local.project
  tags    = local.common_tags
}

module "certificate" {
  source = "./modules/certificate"

  domain  = local.domain
  project = local.project
  zone_id = local.prod_zone_id
  tags    = local.common_tags
}

module "redirect" {
  source = "./modules/redirect"

  domain  = local.domain
  project = local.project
  zone_id = local.prod_zone_id
  tags    = local.common_tags
}

module "load_balancer" {
  source = "./modules/load-balancer"

  aws_acm_certificate = module.certificate.acm_arn
  domain              = local.domain
  lb_subnet_ids       = module.network.public_subnet_ids
  prod_zone_id        = local.prod_zone_id
  project             = local.project
  vpc_id              = module.network.vpc_id
  tags                = local.common_tags
}

module "database" {
  source = "./modules/database"

  db_name           = var.db_name
  db_password       = var.db_password
  db_username       = var.db_username
  project           = local.project
  subnet_group_name = module.network.private_subnet_group_name
  vpc_id            = module.network.vpc_id
  tags              = local.common_tags
}

module "cluster" {
  source = "./modules/cluster"

  lb_security_group = module.load_balancer.security_group
  project           = local.project
  vpc_id            = module.network.vpc_id
  tags              = local.common_tags
}

resource "aws_ecr_repository" "main" {
  name                 = "${local.project}-django-app"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  tags = local.common_tags
}

locals {
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
      value = module.database.address
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
      name  = "CLOUDFRONT_DIST"
      value = module.bucket.cloudfront_domain
    },
    {
      name  = "S3_BUCKET_NAME"
      value = module.bucket.bucket_name
    },
    {
      name  = "SPOTIFY_CLIENT_ID"
      value = var.spotify_client_id
    },
    {
      name  = "SPOTIFY_CLIENT_SECRET"
      value = var.spotify_client_secret
    },
    {
      name  = "YOUTUBE_API_KEY"
      value = var.youtube_api_key
    }
  ]
}

resource "aws_iam_role" "task_role" {
  name = "${local.project}-ecs-task-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_policy" "full_s3_access" {
  name        = "${local.project}-s3-full-access"
  description = "Policy granting full S3 access (Put, Get, Delete, List) to a specific bucket and its objects."
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:HeadObject",
          "s3:ListBucket"
        ],
        Resource = [
          module.bucket.bucket_arn,
          "${module.bucket.bucket_arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "task_role_policy_attachment" {
  role       = aws_iam_role.task_role.name
  policy_arn = aws_iam_policy.full_s3_access.arn
}

module "web" {
  source = "./modules/service"

  cluster            = module.cluster.cluster
  env_variables      = local.env_variables
  execution_role_arn = module.cluster.execution_role_arn
  project            = local.project
  region             = local.region
  repository_url     = aws_ecr_repository.main.repository_url
  security_groups = [
    module.network.default_security_group,
    module.database.security_group,
    module.cluster.security_group
  ]
  service = {
    name                = "web"
    command             = ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "researchbrowserproject.wsgi:application"]
    schedule_expression = null
  }
  service_subnet_ids = module.network.public_subnet_ids
  target_group_arn   = module.load_balancer.target_group_arn
  task_role_arn      = aws_iam_role.task_role.arn
  vpc_id             = module.network.vpc_id
  tags               = local.common_tags
}

module "workers" {
  for_each = { for worker in local.workers : worker.name => worker }

  source = "./modules/service"

  cluster            = module.cluster.cluster
  env_variables      = local.env_variables
  execution_role_arn = module.cluster.execution_role_arn
  project            = local.project
  region             = local.region
  repository_url     = aws_ecr_repository.main.repository_url
  security_groups = [
    module.network.default_security_group,
    module.database.security_group,
    module.cluster.security_group
  ]
  service = {
    name                = each.key
    command             = each.value.command
    schedule_expression = each.value.schedule_expression
  }
  service_subnet_ids = module.network.public_subnet_ids
  target_group_arn   = module.load_balancer.target_group_arn
  vpc_id             = module.network.vpc_id
  tags               = local.common_tags
}

module "ci_cd_pipeline" {
  source = "./modules/ci_cd_pipeline"

  bucket_arn         = module.bucket.bucket_arn
  cloudfront_arn     = module.bucket.cloudfront_arn
  ecr_repository_arn = aws_ecr_repository.main.arn
  github_repository  = "repo:MaxE99/finbrowser:*"
  project            = local.project
  service_arn        = module.web.service_arn
  tags               = local.common_tags
}

# module "bastion_host" {
#   source = "./modules/bastion"

#   project        = var.project
#   public_ssh_key = file(var.public_ssh_key_file_path)
#   security_groups = [
#     module.network.default_security_group,
#     module.database.security_group
#   ]
#   subnet_id = module.network.public_subnet_ids[0]
#   vpc_id    = module.network.vpc_id
# }