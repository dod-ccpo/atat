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

#module "k8s" {
#  source              = "../../modules/k8s"
#  region              = var.region
#  name                = var.name
#  environment         = var.environment
#  owner               = var.owner
#  k8s_dns_prefix      = var.k8s_dns_prefix
#  k8s_node_size       = var.k8s_node_size
#  vnet_subnet_id      = module.vpc.subnet_list["aks"].id
#  enable_auto_scaling = true
#  max_count           = 5
#  min_count           = 3
#  client_id           = data.azurerm_key_vault_secret.k8s_client_id.value
#  client_secret       = data.azurerm_key_vault_secret.k8s_client_secret.value
#  workspace_id        = module.logs.workspace_id
#  vnet_id             = module.vpc.id
#}

module "k8s" {
  source                 = "../../modules/k8s-arm"
  region                 = var.region
  name                   = var.name
  environment            = var.environment
  owner                  = var.owner
  k8s_dns_prefix         = var.k8s_dns_prefix
  k8s_node_size          = var.k8s_node_size
  k8s_network_plugin     = var.k8s_network_plugin
  vnet_subnet_id         = module.vpc.subnet_list["aks"].id
  enable_auto_scaling    = true
  enable_private_cluster = true
  enable_rbac            = true
  max_count              = 4
  min_count              = 3
  node_count             = 3

  client_id           = data.azurerm_key_vault_secret.k8s_client_id.value
  client_secret       = data.azurerm_key_vault_secret.k8s_client_secret.value
  principal_object_id = data.azurerm_key_vault_secret.k8s_object_id.value
  workspace_id        = module.logs.workspace_id

  service_cidr       = "10.2.0.0/16" # Need to decide these values for advanced networking
  dns_service_ip     = "10.2.0.10"
  docker_bridge_cidr = "172.16.0.1/16"
}
