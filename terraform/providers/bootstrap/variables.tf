variable "environment" {}

variable "region" {}

variable "backup_region" {}



variable "owner" {}

variable "name" {}



variable "admin_users" {
type = map
}

variable "storage_admin_whitelist" {
  type = map
}





variable "tenant_id" {}


variable "admin_user_whitelist" { type = map}

variable "networks" { type = map}

variable "virtual_network"{}
variable "route_tables"{ type = map}
variable "dns_servers" {
type = list
}
variable "service_endpoints" { type = map }
variable "routes" { type = map }
variable "storage_container_name" {}
