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

variable "k8s_dns_prefix" {
  type        = string
  description = "A DNS prefix"
}

variable "k8s_node_size" {
  type        = string
  description = "The size of the instance to use in the node pools for k8s"
  default     = "Standard_A1_v2"
}

variable "vnet_subnet_id" {
  description = "Subnet to use for the default k8s pool"
  type        = string
}

variable "enable_auto_scaling" {
  default     = false
  type        = string
  description = "Enable or disable autoscaling (Default: false)"
}

variable "max_count" {
  default     = 1
  type        = string
  description = "Maximum number of nodes to use in autoscaling. This requires `enable_auto_scaling` to be set to true"

}

variable "min_count" {
  default     = 1
  type        = string
  description = "Minimum number of nodes to use in autoscaling. This requires `enable_auto_scaling` to be set to true"
}

variable "client_id" {
  type        = string
  description = "The client ID for the Service Principal associated with the AKS cluster."
}

variable "client_secret" {
  type        = string
  description = "The client secret for the Service Principal associated with the AKS cluster."
}

variable "client_object_id" {
  type        = string
  description = "The client object_id for the Service Principal associated with the AKS cluster."
}

variable "workspace_id" {
  description = "Log Analytics workspace for this resource to log to"
  type        = string
}

variable "vnet_id" {
  description = "The ID of the VNET that the AKS cluster app registration needs to provision load balancers in"
  type        = string
}

variable "private_cluster_enabled" {
  description = "Enable or disable PrivateLink"
  default     = false
  type        = bool
}
