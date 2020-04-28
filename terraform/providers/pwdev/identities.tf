module "keyvault_reader_identity" {
  source      = "../../modules/managed_identity"
  name        = var.name
  owner       = var.owner
  environment = var.environment
  region      = var.region
  identity    = "${var.name}-${var.environment}-vault-reader"
  roles       = ["Reader", "Managed Identity Operator"]

}
