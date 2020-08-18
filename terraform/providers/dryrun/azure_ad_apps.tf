module "tenant_keyvault_app" {
  source = "../../modules/azure_ad"
  name   = "tenant-keyvault"
}
