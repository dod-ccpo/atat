



module "keyvault" {
  source             = "../../modules/keyvault"
  name               = "cz"
  region             = var.region
  owner              = var.owner
  environment        = local.environment
  tenant_id          = var.tenant_id
  principal_id_count = 1
  principal_id       = module.keyvault_reader_identity.principal_id
  admin_principals   = merge(var.admin_users, { "${local.ops_sp_url_to_name}" : var.OPS_OID })
  tenant_principals  = {}
  policy             = "Deny"
  subnet_ids         = [module.vpc.subnet_list["aks"].id, module.bastion.mgmt_subnet_id, var.deployment_subnet_id]
  whitelist          = var.admin_user_whitelist
  workspace_id       = module.logs.workspace_id
  tls_cert_path      = var.tls_cert_path
}

module "tenant_keyvault" {
  source            = "../../modules/keyvault"
  name              = "tenants"
  region            = var.region
  owner             = var.owner
  environment       = local.environment
  tenant_id         = var.tenant_id
  principal_id      = ""
  tenant_principals = { "${module.tenant_keyvault_app.name}" = "${module.tenant_keyvault_app.sp_object_id}" }
  admin_principals  = {}
  policy            = "Deny"
  subnet_ids        = [module.vpc.subnet_list["aks"].id]
  whitelist         = var.admin_user_whitelist
  workspace_id      = module.logs.workspace_id

}
