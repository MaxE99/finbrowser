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

variable "youtube_api_key" {
  type        = string
  sensitive   = true
  description = "YouTube API Key for accessing YouTube data via the API."
}