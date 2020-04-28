data "azurerm_key_vault_secret" "postgres_username" {
  name         = "postgres-root-user"
  key_vault_id = module.operator_keyvault.id
}

data "azurerm_key_vault_secret" "postgres_password" {
  name         = "postgres-root-password"
  key_vault_id = module.operator_keyvault.id
}

module "sql" {
  source                       = "../../modules/postgres"
  name                         = var.name
  owner                        = var.owner
  environment                  = var.environment
  region                       = var.region
  subnet_id                    = module.vpc.subnet_list["aks"].id
  administrator_login          = data.azurerm_key_vault_secret.postgres_username.value
  administrator_login_password = data.azurerm_key_vault_secret.postgres_password.value
  workspace_id                 = module.logs.workspace_id
}
