variable "deployment_location" {
  type        = string
  default     = "East US"
  description = "Azure region in which deployment resources are provisioned."
}

variable "deployment_namespace" {
  type        = string
  default     = "dev"
  description = "Namespace of provisioned deployment resources."
}
