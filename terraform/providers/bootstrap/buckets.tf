# TF State should be restricted to admins only, but IP protected
# This has to be public due to a chicken/egg issue of VPN not
# existing until TF is run. If this bucket is private, you would
# not be able to access it when running TF without being on a VPN.
module "tf_state" {
  source                 = "../../modules/bucket"
  service_name           = "${var.name}${var.environment}tfstate"
  owner                  = var.owner
  name                   = var.name
  environment            = var.environment
  region                 = var.region
  policy                 = "Deny"
  subnet_ids             = []
  whitelist              = var.storage_admin_whitelist
  account_kind           = "Storage"
  storage_container_name = var.storage_container_name
}
