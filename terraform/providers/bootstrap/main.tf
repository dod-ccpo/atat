data "http" "myip" {
  url = "http://ipinfo.io/ip"
}

locals {
  operations_container_registry_name = data.terraform_remote_state.previous_stage.outputs.operations_container_registry_name
  operations_container_registry_login_server = data.terraform_remote_state.previous_stage.outputs.operations_container_registry_login_server
  operations_deployment_subnet_id    = data.terraform_remote_state.previous_stage.outputs.operations_deployment_subnet_id
  operations_storage_account_name    = data.terraform_remote_state.previous_stage.outputs.operations_storage_account_name
  operations_resource_group_name    = data.terraform_remote_state.previous_stage.outputs.operations_resource_group_name
}

resource "azurerm_resource_group" "ops" {
  name     = "${var.deployment_namespace}-ops"
  location = var.deployment_location
}

# TF State should be restricted to admins only, but IP protected
# This has to be public due to a chicken/egg issue of VPN not
# existing until TF is run. If this bucket is private, you would
# not be able to access it when running TF without being on a VPN.
module "tf_state" {
  source                 = "../../modules/bucket"
  service_name           = "czops${var.deployment_namespace}tfstate"
  owner                  = "remove_me"
  name                   = "${var.deployment_namespace}bucket"
  environment            = var.deployment_namespace
  region                 = var.deployment_location
  policy                 = "Deny"
  subnet_ids             = [local.operations_deployment_subnet_id]
  whitelist              = { "operator" : chomp(data.http.myip.body) }
  account_kind           = "Storage"
  storage_container_name = local.operations_storage_account_name
}
