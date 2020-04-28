variable "environment" {}

variable "region" {}

variable "backup_region" {}


variable "owner" {}

variable "name" {}

variable "virtual_network" {}


variable "networks" {
  type = map
}

variable "service_endpoints" {
  type = map
}

variable "route_tables" {
  description = "Route tables and their default routes"
  type        = map
}

# Custom routes
variable "routes" {
  description = "Routes for next hop types: VirtualNetworkGateway, VnetLocal, Internet or None"
  type        = map
}

variable "dns_servers" {
  type = list
}

variable "k8s_node_size" {}

variable "k8s_dns_prefix" {}

variable "tenant_id" {}

variable "admin_users" {
  type = map
}

variable "admin_user_whitelist" {
  type = map
}

variable "storage_admin_whitelist" {
  type = map
}

variable "vpn_client_cidr" {
  type = list
}
