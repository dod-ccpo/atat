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
  whitelist              = merge(var.storage_admin_whitelist,{ "${data.azurerm_client_config.current.client_id}": chomp(data.http.myip.body) })
  bucket_cors_properties = var.bucket_cors_properties
  storage_container_name = var.task_order_bucket_storage_container_name
  depends_on    = [module.vpc]
}
