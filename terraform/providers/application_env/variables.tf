variable "deployment_location" {
  type        = string
  description = "Azure region in which deployment resources are provisioned."
  default     = "East US"
}

variable "region" {
  type        = string
  description = "Azure region in which deployment resources are provisioned - short name"
  default     = "eastus"
}

variable "deployment_namespace" {
  type        = string
  description = "Namespace of provisioned deployment resources."
}

variable "owner" {
  type        = string
  default     = "promptworks"
  description = "TODO(jesse) Is this a required property in all those modules?"
}

variable "name" {
  type        = string
  default     = "cloudzero"
  description = "TODO(jesse) Is this a required property in all those modules?"
}

variable "virtual_network" {
  type        = string
  description = ""
  default     = "10.1.0.0/16"
}

variable "networks" {
  type        = map
  description = ""
  default     = {}
}

variable "service_endpoints" {
  type        = map
  description = ""
  default     = {}
}

variable "route_tables" {
  type        = map
  description = "Route tables and their default routes"
  default     = {}
}

variable "routes" {
  type        = map
  description = "Routes for next hop types: VirtualNetworkGateway, VnetLocal, Internet or None"
  default     = {}
}

variable "k8s_node_size" {
  type        = string
  description = ""
  default     = "Standard_D2_v2"
}

variable "k8s_dns_prefix" {
  type        = string
  description = ""
  default     = "atat"
}

variable "private_k8s_subnet_cidr" {
  type        = string
  default     = "10.1.5.0/24"
  description = ""
}

variable "private_aks_service_dns" {
  default = "10.254.253.10"
}

variable "private_aks_service_cidr" {
  default = "10.254.253.0/24"
}

variable "private_aks_docker_bridge_cidr" {
  default = "172.17.0.1/16"
}

variable "private_aks_sp_secret" {
  default = "sdfasdfasf"
}

variable "private_aks_sp_id" {
  default = "asdfasdfasd"
}

variable "aks_max_node_count" {
  type        = number
  description = ""
  default     = 5
}

variable "aks_min_node_count" {
  type        = number
  description = ""
  default     = 3
}

variable "task_order_bucket_storage_container_name" {
  type        = string
  description = ""
  default     = "task-order-pdfs"
}

# TODO: Use the bootstrap data for this value
variable "tf_state_storage_container_name" {
  type        = string
  description = ""
  default     = "tf-application"
}

variable "virtual_appliance_routes" {
  type        = map
  description = ""
  default     = {}
}

variable "virtual_appliance_route_tables" {
  type        = map
  description = ""
  default = {
    "aks" = "VirtualAppliance"
  }
}

variable "tls_cert_path" {
  type        = string
  description = "Long-lived certificate for atat.dev and *.atat.dev."
  default     = "/tmp/atatdev.pem"
}

variable "dhparams_path" {
  type        = string
  description = "Long-lived certificate for hyper-securing our session encryption"
  default     = "/tmp/dhparams.pem"
}
variable "keyvault_secrets" {
  type        = map
  description = "Variables used to configure the kubernetes cluster, loaded into keyvault."
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

variable "ops_resource_group" {
  type = string
}
variable "ops_storage_account" {
  type = string
}

variable "tf_bootstrap_container" {
  type = string
}
variable "ddos_enabled" {
  description = "Enable or disable DDoS Protection (1,0)"
  default     = "0"
}
variable "aks_internal_lb_ip" {
  type        = string
  description = "The IP of the loadbalancer that will be created by k8s"
  default     = "10.1.2.201"
}

variable "maintenance_page_ip" {
  type        = string
  description = "The IP of the loadbalancer that will be created by k8s"
  default     = "10.1.2.203"
}
