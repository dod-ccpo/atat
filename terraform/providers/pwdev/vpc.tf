


data "azurerm_route_table" "aks_route_table" {
  name                = var.name
  resource_group_name = module.k8s.k8s_resource_group_id
}



module "vpc" {
  source            = "../../modules/vpc/"
  environment       = var.environment
  region            = var.region
  virtual_network   = var.virtual_network
  networks          = var.networks
  route_tables      = merge(var.route_tables,{"aks" = }
  owner             = var.owner
  name              = var.name
  dns_servers       = var.dns_servers
  service_endpoints = var.service_endpoints
  custom_routes     = var.routes
}
