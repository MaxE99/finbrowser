variable "project" {
  type        = string
  description = "The name of the project."
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to all resources."
}