# TF State should be restricted to admins only, but IP protected
# This has to be public due to a chicken/egg issue of VPN not
# existing until TF is run. If this bucket is private, you would
# not be able to access it when running TF without being on a VPN.
module "tf_state" {
  source                 = "../../modules/bucket"
  service_name           = "${var.name}${local.environment}tfstate"
  owner                  = var.owner
  name                   = var.name
  environment            = local.environment
  region                 = var.region
  policy                 = "Deny"
  subnet_ids             = []
  whitelist              = merge(var.storage_admin_whitelist, { "operator" : chomp(data.http.myip.body) },{ "opsnet": var.virtual_network })
  account_kind           = "Storage"
  storage_container_name = var.storage_container_name
}
