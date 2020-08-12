variable "region" {
  type        = string
  description = "Region this module and resources will be created in"
}

variable "name" {
  type        = string
  description = "Unique name for the services in this module"
}

variable "environment" {
  type        = string
  description = "Environment these resources reside (prod, dev, staging, etc)"
}

variable "owner" {
  type        = string
  description = "Owner of the environment and resources created in this module"
}

variable "capacity" {
  type        = string
  default     = 1
  description = "The capacity of the redis cache"
}

variable "family" {
  type        = string
  default     = "C"
  description = "The subscription family for redis"
}

variable "sku_name" {
  type        = string
  default     = "Standard"
  description = "The sku to use"
}

variable "enable_non_ssl_port" {
  type        = bool
  default     = false
  description = "Enable non TLS port (default: false)"
}

variable "minimum_tls_version" {
  type        = string
  default     = "1.2"
  description = "Minimum TLS version to use"
}

variable "enable_authentication" {
  type        = bool
  default     = true
  description = "Enable or disable authentication (default: true)"
}

variable "subnet_id" {
  type        = string
  description = "Subnet ID that the service_endpoint should reside"
}

variable "workspace_id" {
  description = "Log Analytics workspace for this resource to log to"
  type        = string
}

variable "pet_name" {}
