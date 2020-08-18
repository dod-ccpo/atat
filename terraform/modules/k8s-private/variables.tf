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

variable "rg" {}

variable "vpc_name" {}

variable "vpc_address_space" {}

variable "aks_subnet_id" {}

variable "subnet_cidr" {}

variable "aks_ssh_pub_key_path" {}

variable "service_dns" {}

variable "docker_bridge_cidr" {}

variable "service_cidr" {}

variable "private_aks_sp_id" {}

variable "private_aks_sp_secret" {}

variable "log_analytics_workspace_id" {}



variable "k8s_dns_prefix" {
  type        = string
  description = "A DNS prefix"
}

variable "k8s_node_size" {
  type        = string
  description = "The size of the instance to use in the node pools for k8s"
  default     = "Standard_A1_v2"
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




variable "vnet_id" {
  description = "The ID of the VNET that the AKS cluster app registration needs to provision load balancers in"
  type        = string
}

variable "private_cluster_enabled" {
  description = "Enable or disable PrivateLink"
  default     = false
  type        = bool
}
