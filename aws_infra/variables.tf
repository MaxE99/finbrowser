variable "domain" {
  type        = string
  default     = "finbrowser.io"
  description = "The domain name for the project, used for DNS configuration."
}

variable "db_name" {
  type        = string
  sensitive   = true
  description = "The name of the database to create within the database instance."
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "The password for the database user."
}

variable "db_username" {
  type        = string
  sensitive   = true
  description = "The username for the database, which will have access to the specified database."
}

variable "email_host_password" {
  type        = string
  sensitive   = true
  description = "The password for the email host user."
}

variable "email_host_user" {
  type        = string
  sensitive   = true
  description = "The username for the email host."
}

variable "public_ssh_key_file_path" {
  type        = string
  default     = ""
  description = "The file path to the public SSH key for accessing resources."
}

variable "prod_zone_id" {
  type        = string
  default     = "Z0063739EBD6ODRQ14EA"
  description = "The ID of the Route 53 hosted zone for the production environment, used for DNS record management."
}

variable "project" {
  type        = string
  default     = "finbrowser"
  description = "The name of the project."
}

variable "region" {
  type        = string
  default     = "us-east-2"
  description = "The AWS region where the resources will be created, which determines resource availability and proximity."
}

variable "secret_key" {
  type        = string
  sensitive   = true
  description = "The secret key used for authentication and encryption purposes."
}

variable "spotify_client_id" {
  type        = string
  sensitive   = true
  description = "Spotify Client ID for authenticating API requests."
}

variable "spotify_client_secret" {
  type        = string
  sensitive   = true
  description = "Spotify Client Secret for securing API requests."
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
  description = "A list of worker configurations, each with a name, command to execute, and schedule for execution."
}

variable "youtube_api_key" {
  type        = string
  sensitive   = true
  description = "YouTube API Key for accessing YouTube data via the API."
}