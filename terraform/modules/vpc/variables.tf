variable "deployment_namespace" {
  description = "Environment (Prod,Dev,etc)"
}

variable "deployment_location" {
  description = "Region (useast2, etc)"

}

variable "name" {
  description = "Name or prefix to use for all resources created by this module"
}

variable "owner" {
  description = "Owner of these resources"

}


variable "virtual_network" {
  description = "The supernet used for this VPC a.k.a Virtual Network"
  type        = string
  default     = "10.1.0.0/16"
}

# variable "networks" {
#   description = "A map of lists describing the network topology"
#   type        = map
# }

variable "dns_servers" {
  description = "DNS Server IPs for internal and public DNS lookups (must be on a defined subnet)"
  type        = list
}

# variable "route_tables" {
#   type        = map
#   description = "A map with the route tables to create"
# }

# variable "service_endpoints" {
#   type        = map
#   description = "A map of the service endpoints and its mapping to subnets"

# }

# variable "routes" {
#   type        = map
#   description = "A map of custom routes"
# }

# variable "virtual_appliance_routes" {}

# variable "virtual_appliance_route_tables" {}
