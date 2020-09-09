data "azurerm_client_config" "current" {}


module "keyvault" {
  source            = "../../modules/keyvault"
  name              = "cz"
  region            = var.region
  owner             = var.owner
  environment       = var.environment
  tenant_id         = var.tenant_id
  principal_id      = module.keyvault_reader_identity.principal_id
  admin_principals  = merge(var.admin_users, { "operator" : var.OPS_CID, "ops_sp" : module.ops_keyvault_app.sp_object_id })
  tenant_principals = {}
  policy            = "Deny"
  subnet_ids        = [module.vpc.subnet_list["aks"].id, module.bastion.mgmt_subnet_id]
  whitelist         = var.admin_user_whitelist
  workspace_id      = module.logs.workspace_id
  pet_name          = random_pet.unique_id.id
}

module "tenant_keyvault" {
  source            = "../../modules/keyvault"
  name              = "tenants"
  region            = var.region
  owner             = var.owner
  environment       = var.environment
  tenant_id         = var.tenant_id
  principal_id      = ""
  tenant_principals = { "${module.tenant_keyvault_app.name}" = "${module.tenant_keyvault_app.sp_object_id}" }
  admin_principals  = {}
  policy            = "Deny"
  subnet_ids        = [module.vpc.subnet_list["aks"].id]
  whitelist         = var.admin_user_whitelist
  workspace_id      = module.logs.workspace_id
  pet_name          = random_pet.unique_id.id
}
