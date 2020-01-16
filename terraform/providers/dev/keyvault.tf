module "keyvault" {
  source       = "../../modules/keyvault"
  name         = var.name
  region       = var.region
  owner        = var.owner
  environment  = var.environment
  tenant_id    = var.tenant_id
  principal_id = "f9bcbe58-8b73-4957-aee2-133dc3e58063"
}
