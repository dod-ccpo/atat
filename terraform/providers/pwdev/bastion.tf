

module "bastion" {

  source                  = "../../modules/bastion"
  rg                      = "${var.name}-${var.environment}-jump"
  region                  = var.region
  mgmt_subnet_rg          = module.vpc.resource_group_name
  mgmt_subnet_vpc_name    = module.vpc.vpc_name
  bastion_subnet_rg       = module.vpc.resource_group_name
  bastion_subnet_vpc_name = module.vpc.vpc_name
  mgmt_subnet_cidr        = "10.1.254.0/24"
  bastion_subnet_cidr     = "10.1.4.0/24"


}
