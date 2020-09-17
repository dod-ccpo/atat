module "keyvault_reader_identity" {
  source      = "../../modules/managed_identity"
  name        = var.name
  owner       = var.owner
  environment = local.environment
  region      = var.region
  identity    = "${var.name}-${local.environment}-vault-reader"
  roles       = ["Reader", "Managed Identity Operator"]
}
