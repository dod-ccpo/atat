# variable "deployment_namespace" {
#   type        = string
#   default     = "dev"
#   description = "Namespace of provisioned deployment resources."
# }

variable "operations_location" {
  type        = string
  default     = "East US"
  description = "Azure region in which operations resources are provisioned."
}

variable "namespace" {
  type = string
  # default     = "dev"
  description = "Namespace of provisioned operations resources."
}

variable "operator_subscription_id" {
  type = string
}

variable "operator_client_id" {
  type = string
}

variable "operator_client_secret" {
  type = string
}

variable "operator_tenant_id" {
  type = string
}
