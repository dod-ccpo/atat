data "azurerm_key_vault_secret" "k8s_client_id" {
  name         = "k8s-client-id"
  key_vault_id = module.operator_keyvault.id
}

data "azurerm_key_vault_secret" "k8s_client_secret" {
  name         = "k8s-client-secret"
  key_vault_id = module.operator_keyvault.id
}

data "azurerm_key_vault_secret" "k8s_object_id" {
  name         = "k8s-object-id"
  key_vault_id = module.operator_keyvault.id
}

module "k8s" {
  source              = "../../modules/k8s"
  region              = var.region
  name                = var.name
  environment         = var.environment
  owner               = var.owner
  k8s_dns_prefix      = var.k8s_dns_prefix
  k8s_node_size       = var.k8s_node_size
  vnet_subnet_id      = module.vpc.subnet_list["aks"].id
  enable_auto_scaling = true
  max_count           = 5
  min_count           = 3
  client_id           = data.azurerm_key_vault_secret.k8s_client_id.value
  client_secret       = data.azurerm_key_vault_secret.k8s_client_secret.value
  client_object_id    = data.azurerm_key_vault_secret.k8s_object_id.value
  workspace_id        = module.logs.workspace_id
  vnet_id             = module.vpc.id
}
