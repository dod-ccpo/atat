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
  description = "Owner of this environment"
}

variable "tenant_id" {
  type        = string
  description = "The Tenant ID"
}

variable "principal_id" {
  type        = string
  description = "The service principal_id of the k8s cluster"
}
