module "keyvault" {
  source           = "../../modules/keyvault"
  name             = "cz"
  region           = var.region
  owner            = var.owner
  environment      = var.environment
  tenant_id        = var.tenant_id
  principal_id     = "f9bcbe58-8b73-4957-aee2-133dc3e58063"
  admin_principals = var.admin_users
  policy           = "Deny"
  subnet_ids       = [module.vpc.subnet_list["aks"].id]
  whitelist        = var.admin_user_whitelist
  workspace_id     = module.logs.workspace_id
}
