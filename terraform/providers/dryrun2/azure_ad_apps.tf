module "tenant_keyvault_app" {
  source = "../../modules/azure_ad"
  name   = "tenant-keyvault"
}


module "aks_sp" {
  source = "../../modules/azure_ad"
  name   = "aks-service-principal"
}

module "bastion_sp" {
  source = "../../modules/azure_ad"
  name   = "bastion-service-principal"
}

module "ops_keyvault_app" {
  source = "../../modules/azure_ad"
  name   = "ops-keyvault-sp"
}
