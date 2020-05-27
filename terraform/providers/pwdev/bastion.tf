

module "bastion" {

  source                  = "../../modules/bastion"
  rg                      = "${var.name}-${var.environment}-jump"
  region                  = var.region
  mgmt_subnet_rg          = module.vpc.resource_group_name
  mgmt_subnet_vpc_name    = module.vpc.vpc_name
  bastion_subnet_rg       = module.vpc.resource_group_name
  bastion_subnet_vpc_name = module.vpc.vpc_name
  mgmt_subnet_cidr        = "10.1.250.0/24"
  bastion_subnet_cidr     = "10.1.4.0/24"
  bastion_aks_sp_secret   = var.bastion_aks_sp_secret
  bastion_aks_sp_id       = var.bastion_aks_sp_id
  environment             = var.environment
  owner                   = var.owner
  name                    = var.name

  bastion_ssh_pub_key_path   = var.bastion_ssh_pub_key_path
  log_analytics_workspace_id = var.log_analytics_workspace_id


}
