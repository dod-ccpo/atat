# Task order bucket is required to be accessible publicly by the users.
# which is why the policy here is "Allow"
module "task_order_bucket" {
  source                 = "../../modules/bucket"
  service_name           = "${var.environment}tasks"
  owner                  = var.owner
  name                   = var.name
  environment            = var.environment
  region                 = var.region
  policy                 = "Allow"
  subnet_ids             = [module.vpc.subnet_list["aks"].id]
  whitelist              = var.storage_admin_whitelist
  bucket_cors_properties = var.bucket_cors_properties
}

# TF State should be restricted to admins only, but IP protected
# This has to be public due to a chicken/egg issue of VPN not
# existing until TF is run. If this bucket is private, you would
# not be able to access it when running TF without being on a VPN.
module "tf_state" {
  source       = "../../modules/bucket"
  service_name = "cloudzeroddryruntfstate" # change for dry run
  owner        = var.owner
  name         = var.name
  environment  = var.environment
  region       = var.region
  policy       = "Deny"
  subnet_ids   = []
  whitelist    = var.storage_admin_whitelist
  account_kind = "Storage"
}
