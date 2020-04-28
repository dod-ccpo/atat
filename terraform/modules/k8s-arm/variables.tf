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
  default     = "Standard_D4s_v2"
}

variable "os_disk_size_gb" {
  type        = number
  description = "OS disk size of the node. Providing zero picks the default for that node type."
  default     = 0
}

variable "k8s_network_plugin" {
  type    = string
  default = "azure"
}

variable "k8s_version" {
  type    = string
  default = "1.14.8"
}
variable "k8s_zones" {
  description = "Number of Availability Zones for k8s node pool"
  type        = list(string)
  default     = ["1", "2"]
}

variable "vnet_subnet_id" {
  description = "Subnet to use for the default k8s pool"
  type        = string
}

variable "enable_auto_scaling" {
  default     = false
  type        = bool
  description = "Enable or disable autoscaling (Default: false)"
}

variable "enable_private_cluster" {
  default     = false
  type        = bool
  description = "Enable or disable Private cluster (Default: false)"
}


variable "enable_rbac" {
  default     = true
  type        = bool
  description = "Enable or disable RBAC (Default: true)"
}
variable "max_count" {
  default     = 1
  type        = number
  description = "Maximum number of nodes to use in autoscaling. This requires `enable_auto_scaling` to be set to true"

}
variable "node_count" {
  default     = 3
  type        = number
  description = "number of nodes to in the cluster."

}
variable "min_count" {
  default     = 1
  type        = number
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

variable "principal_object_id" {
  type        = string
  description = "The object id of Service Principal associated with the AKS cluster."
}

variable "workspace_id" {
  description = "Log Analytics workspace for this resource to log to"
  type        = string
}

variable "vmss_node_pool" {
  type        = bool
  default     = false
  description = "Boolean flag to describle the agent pool. Defaults to false"
}

variable "service_cidr" {
  type        = string
  description = "Service CIDR associated with the cluster."
}

variable "dns_service_ip" {
  type        = string
  description = "DNS Service IP associated with the cluster."
}

variable "docker_bridge_cidr" {
  type        = string
  description = "DNS Service IP associated with the cluster."
}


