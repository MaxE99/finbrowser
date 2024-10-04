variable "domain" {
  type    = string
  default = "ebert-test-domain.com"
}

variable "db_name" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "db_username" {
  type      = string
  sensitive = true
}

variable "email_host_password" {
  type      = string
  sensitive = true
}

variable "email_host_user" {
  type      = string
  sensitive = true
}

variable "public_ssh_key_file_path" {
  type    = string
  default = ""
}

variable "prod_zone_id" {
  type    = string
  default = "Z03766462O143CYRIVTVM"
}

variable "project" {
  type    = string
  default = "finbrowser"
}

variable "region" {
  type    = string
  default = "us-east-2"
}

variable "secret_key" {
  type      = string
  sensitive = true
}

variable "workers" {
  type = list(object({
    name                = string
    command             = list(string)
    schedule_expression = string
  }))
  default = [
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
      name                = "forbes"
      command             = ["python", "manage.py", "scrape_forbes"]
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
}