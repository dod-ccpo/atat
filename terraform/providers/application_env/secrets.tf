module "operator_keyvault" {
  source            = "../../modules/keyvault"
  name              = "ops"
  region            = var.region
  owner             = var.owner
  environment       = local.environment
  tenant_id         = var.tenant_id
  principal_id      = ""
  admin_principals  = merge(var.admin_users, { "TerraformOperator" = "${var.OPS_OID}" })
  tenant_principals = { "${module.ops_keyvault_app.name}" = "${module.ops_keyvault_app.sp_object_id}" }
  policy            = "Deny"
  subnet_ids        = [module.vpc.subnet_list["aks"].id, module.bastion.mgmt_subnet_id, var.deployment_subnet_id]
  whitelist         = var.admin_user_whitelist
  workspace_id      = module.logs.workspace_id
}
