

module "vpc" {
  source                         = "../../modules/vpc/"
  environment                    = local.environment
  region                         = var.region
  virtual_network                = var.virtual_network
  networks                       = var.networks
  route_tables                   = var.route_tables
  owner                          = var.owner
  name                           = var.name
  dns_servers                    = var.dns_servers
  service_endpoints              = var.service_endpoints
  custom_routes                  = var.routes
  virtual_appliance_routes       = "${var.virtual_appliance_routes["aks-private"]},${module.private-aks-firewall.ip_config[0].private_ip_address}"
  virtual_appliance_route_tables = var.virtual_appliance_route_tables

}
