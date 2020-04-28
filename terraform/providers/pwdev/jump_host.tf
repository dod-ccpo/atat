module "jump_host" {
  source      = "../../modules/jump_host/"
  name        = var.name
  owner       = var.owner
  environment = var.environment
  region      = var.region
  subnet_id   = module.vpc.subnet_list["edge"].id
}
