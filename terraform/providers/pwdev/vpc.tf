




module "vpc" {
  source            = "../../modules/vpc/"
  environment       = var.environment
  region            = var.region
  virtual_network   = var.virtual_network
  networks          = var.networks
  route_tables      = var.route_tables
  owner             = var.owner
  name              = var.name
  dns_servers       = var.dns_servers
  service_endpoints = var.service_endpoints
  custom_routes     = var.routes
}
