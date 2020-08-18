




module "bastion" {



  source                     = "../../modules/bastion"
  rg                         = "${var.name}-${var.environment}-jump"
  region                     = var.region
  mgmt_subnet_rg             = module.vpc.resource_group_name
  mgmt_subnet_vpc_name       = module.vpc.vpc_name
  bastion_subnet_rg          = module.vpc.resource_group_name
  bastion_subnet_vpc_name    = module.vpc.vpc_name
  mgmt_subnet_cidr           = "10.1.250.0/24"
  bastion_subnet_cidr        = "10.1.4.0/24"
  bastion_aks_sp_secret      = module.bastion_sp.application_password
  bastion_aks_sp_id          = module.bastion_sp.application_id
  environment                = var.environment
  owner                      = var.owner
  name                       = var.name
  bastion_ssh_pub_key_path   = var.bastion_ssh_pub_key_path
  log_analytics_workspace_id = module.logs.workspace_id
  depends_on                 = [module.vpc]



}
