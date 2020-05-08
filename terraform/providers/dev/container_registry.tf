module "container_registry" {
  source        = "../../modules/container_registry"
  name          = var.name
  region        = var.region
  environment   = var.environment
  owner         = var.owner
  backup_region = var.backup_region
  policy        = "Deny"
  subnet_ids    = [module.vpc.subnet_list["private"].id]
  whitelist     = var.admin_user_whitelist
  workspace_id  = module.logs.workspace_id
}
