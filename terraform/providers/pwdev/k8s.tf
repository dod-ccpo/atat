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


data "azurerm_route_table" "auto_gen_k8s" {

  name                = "aks-agentpool-54410534-routetable"
  resource_group_name = module.k8s.k8s_resource_group_id
}

output "k8s_rt" { value = data.azurerm_route_table.auto_gen_k8s.id }
output "aks_sub_id" { value = module.vpc.subnet_list["aks"].id }

resource "azurerm_subnet_route_table_association" "k8s_aks_route_table" {

  subnet_id      = module.vpc.subnet_list["aks"].id
  route_table_id = data.azurerm_route_table.auto_gen_k8s.id

}

#"aks"   = "aks,to_vnet,10.1.0.0/16,VnetLocal"

resource "azurerm_route" "custom_routes" {
  name                = "${var.name}-${var.environment}-to_vnet"
  resource_group_name = module.k8s.k8s_resource_group_id
  route_table_name    = "aks-agentpool-54410534-routetable"
  address_prefix      = "10.1.0.0/16"
  next_hop_type       = "VnetLocal"
}
