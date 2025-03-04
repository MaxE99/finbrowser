variable "domain" {
  type        = string
  description = "The domain name associated with the project, used for DNS configuration and resource access."
}

variable "project" {
  type        = string
  description = "The name of the project."
}

variable "zone_id" {
  type        = string
  description = "The ID of the DNS zone in which the domain is managed. This is required for configuring DNS records."
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to all resources."
}