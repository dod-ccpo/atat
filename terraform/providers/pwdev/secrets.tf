module "operator_keyvault" {
  source           = "../../modules/keyvault"
  name             = "ops"
  region           = var.region
  owner            = var.owner
  environment      = var.environment
  tenant_id        = var.tenant_id
  principal_id     = ""
  admin_principals = var.admin_users
  app_principals   = {}
  policy           = "Deny"
  subnet_ids       = [module.vpc.subnet_list["aks"].id]
  whitelist        = var.admin_user_whitelist
  workspace_id     = module.logs.workspace_id
}
