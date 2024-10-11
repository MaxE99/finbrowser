module "bucket" {
  source = "./modules/bucket"

  domain  = "https://${var.domain}"
  project = var.project
}

module "network" {
  source = "./modules/network"

  project = var.project
}

module "certificate" {
  source = "./modules/certificate"

  domain  = var.domain
  project = var.project
  zone_id = var.prod_zone_id
}

module "load_balancer" {
  source = "./modules/load-balancer"

  aws_acm_certificate = module.certificate.acm_arn
  domain              = var.domain
  lb_subnet_ids       = module.network.public_subnet_ids
  prod_zone_id        = var.prod_zone_id
  project             = var.project
  vpc_id              = module.network.vpc_id
}

module "database" {
  source = "./modules/database"

  db_name           = var.db_name
  db_password       = var.db_password
  db_username       = var.db_username
  project           = var.project
  subnet_group_name = module.network.private_subnet_group_name
  vpc_id            = module.network.vpc_id
}

module "cluster" {
  source = "./modules/cluster"

  lb_security_group = module.load_balancer.security_group
  project           = var.project
  vpc_id            = module.network.vpc_id
}

resource "aws_ecr_repository" "main" {
  name                 = "${var.project}-django-app"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  tags = {
    Project     = var.project
    Name        = "ECR Repository"
    Description = "Image of the Django app for the cluster to spin up and execute"
  }
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
      name  = "S3_BUCKET"
      value = module.bucket.bucket_url
    }
  ]
}

module "web" {
  source = "./modules/service"

  cluster            = module.cluster.cluster
  env_variables      = local.env_variables
  execution_role_arn = module.cluster.execution_role_arn
  project            = var.project
  region             = var.region
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
  vpc_id             = module.network.vpc_id
}

module "workers" {
  for_each = { for worker in var.workers : worker.name => worker }

  source = "./modules/service"

  cluster            = module.cluster.cluster
  env_variables      = local.env_variables
  execution_role_arn = module.cluster.execution_role_arn
  project            = var.project
  region             = var.region
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