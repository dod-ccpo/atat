data "http" "myip" {
  url = "http://ipinfo.io/ip"
}

data "terraform_remote_state" "bootstrap_new_tenant_state" {
  backend = "local"

  config = {
    path = "../bootstrap_new_tenant/terraform.tfstate"
  }
}

locals {
  operations_container_registry_name = data.terraform_remote_state.bootstrap_new_tenant_state.outputs.operations_container_registry_name
  operations_deployment_subnet_id    = data.terraform_remote_state.bootstrap_new_tenant_state.outputs.operations_deployment_subnet_id
  operations_storage_account_name    = data.terraform_remote_state.bootstrap_new_tenant_state.outputs.operations_storage_account_name
}

resource "azurerm_resource_group" "ops" {
  name     = "${var.deployment_namespace}-ops"
  location = var.deployment_location
}

resource "azurerm_container_registry" "ops" {
  name                = "opscontainerregistry${var.deployment_namespace}"
  resource_group_name = azurerm_resource_group.ops.name
  location            = azurerm_resource_group.ops.location
  sku                 = "Premium"
  admin_enabled       = false

  network_rule_set {
    default_action = "Allow"
    ip_rule        = []
  }
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
