provider "azurerm" {
  version = "=2.19.0"
  features {}

}

provider "azuread" {
  # Whilst version is optional, we /strongly recommend/ using it to pin the version of the Provider being used
  version = "=0.11.0"
}

terraform {
  backend "azurerm" {}
}

resource "random_pet" "unique_id" {

  length    = 1
  separator = ""

}

locals {

  ops_sp_url_to_name           = replace(var.OPS_SP_URL, "http://", "")
  environment                  = length(var.environment) > 0 ? var.environment : random_pet.unique_id.id
  private_aks_appliance_routes = var.virtual_appliance_routes["aks-private"]



}
